# injector.py
# =====================================================
# This module is used to inject the Smali Code provided
# by arg_parser.py inside the decompiled APK we get from
# apktool_interface.py.
# If the script is executed with 'manual injection' 
# arguments, the decompiled_directory on which inject
# the smali on will be defined in smali_baker.py
# =====================================================

from commands import apktool_interface
from commands import utilities
from commands import arg_parser
from os import path
from os import walk
from xml.dom.minidom import parseString

global activity_name

def detect_decompiled_directory():
    """
    detect_decompiled_directory() checks if the global variable decompiled_directory is set or not.
    Kills execution in case of errors.
    """
    try:
        apktool_interface.decompiled_directory
        return True
    except AttributeError:
        print("[!] Couldn't detect the decompiled APK directory, did you edit the code? Global variable is not defined [!]")
        utilities.quit()
    except Exception as e:
        print("[!] Unexpected error detected [!]")
        print("Exception: \n ===========")
        print(e)
        utilities.quit()

def read_AndroidManifest():
    """
    read_AndroidManifest() reads the AndroidManifest.xml file from the decompiled_directory.
    Searches for common 'activity' names within the file, if they are found we recursively
    dig the XML file to find the MAIN activity on which we will inject.
    Kills execution in case of errors.  
    """
    global activity_name
    
    detect_decompiled_directory()

    manifest_name = "AndroidManifest.xml"
    manifest_path = path.join(apktool_interface.decompiled_directory, manifest_name)

    data_stream = '' # read data from AndroidManifest
    with open(manifest_path, 'r') as f:
        data_stream = f.read()
    
    # Parse the XML content
    dom = parseString(data_stream)

    try:
        # Potential activity names, spotted by manually decompiling various kind of APKs
        activity_names = ['activity', 'activity-alias']
        for name in activity_names:

            # If the activity hasn't been found in the XML file
            if (dom.getElementsByTagName(name).length == 0): 
                print("[!] No '" + name + "' found in AndroidManifest.xml file [!]")
                continue
            else:
                print("[+] " + name + " found in AndroidManifest.xml file [+]")

            # Store a list of the activities available
            activities = dom.getElementsByTagName(name)

            for activity in activities: # For all the activities available
                # If the APP is built with Unity3D
                if ('com.unity3d' in activity.getAttribute('android:name')):
                    print("[+] Unity3D detected inside the APK [+]")
                    # Set the activity_name so we can inject it
                    activity_name = activity.getAttribute('android:name')
                    break
                # If the APP is using targetActivity tags, found on complex apps such as Spotify
                if (activity.getAttribute('targetActivity') != ""):
                    # Set the activity_name so we can inject it
                    activity_name = activity.getAttribute('android:targetActivity')
                    break

                intents = activity.getElementsByTagName('intent-filter') # Get the <intent-filter>'s
                for intent in intents: 
                    actions = intent.getElementsByTagName('action') # Get the <action>'s
                    for action in actions:
                        categories = intent.getElementsByTagName('category') # Get the <category>'s 
                        for category in categories:
                            # If the <intent-filter> contains an <action> with name android.intent.action.MAIN, and a <category> with name android.intent.category.LAUNCHER
                            if (action.getAttribute('android:name') == 'android.intent.action.MAIN' and category.getAttribute('android:name') == "android.intent.category.LAUNCHER"):
                                # Set the activity_name so we can inject it
                                activity_name = (activity.getAttribute('android:name'))
                                print("[+] Found activity name ==> " + activity_name + "[+]")
    
    # In case of exceptions, print it and then kill execution.
    except Exception as e:
        print("[!] Unexpected error detected [!]")
        print("Exception: \n ===========")
        print(e)
        utilities.quit()


def injectSmali():
    """
    injectSmali() will inject the smali code provided by the user inside the Activity Name preiously found.
    If the 'manual injection' arguments are specified, try to inject it directly.
    Else, search for the Activity Name smali file by building it's path using the android:name we found earlier.
    For each smali file found, try to inject it by first reading it and then overriding its content.
    If the ".locals" variable of the decompiled APK is lower than 15, we will increase it by one.
    Kills execution in case of errors.  
    """
    # Manual Injection, --smali-file and --smali-method arguments specified
    if( (arg_parser.args.smali_file is not None) and (arg_parser.args.smali_method is not None) ):

        # Which smali file we need to inject
        smali_files_available = []
        smali_files_available.append(arg_parser.args.smali_file)

        # Read the custom smali code we should inject and indent it
        input_smali_filestream = open(arg_parser.args.smali)
        code_to_inject = input_smali_filestream.readlines()
        indented_code_to_inject = utilities.indent_smali_code(code_to_inject)
    
        # Read all the lines from the original smali file and then open stream with write permissions.
        # All the previous content will be overridden.
        read_input_smali_file = open(arg_parser.args.smali_file, 'r').readlines()
        write_input_smali_file = open(arg_parser.args.smali_file, 'w')

        # Is the smali method found?
        inject_on_next_line = False

        print("[+] Injecting into custom method " + str(arg_parser.args.smali_method) + " [+]")

        injection_successfull = False # Use later to understand if the injection was done or not
        for line in read_input_smali_file: # for each line
            
            if( (str(arg_parser.args.smali_method) in line) ) : # if the user-specified smali method is in the current line
                inject_on_next_line = True # we will inject our custom smali code next
            
            if(inject_on_next_line == True ): # if we are under the correct smali method
                if('.locals' in line): # we will inject our smali code after the .locals variable
                    split, current_locals_value = line.split() # get the current .locals values in two separate variables

                    # .locals values must be a value between 0 and 15 
                    if(current_locals_value == 15): continue
                    # else increase it to be sure our smali code will work 
                    else:
                        new_locals_value = int(current_locals_value) + 1 # increase
                    
                    write_input_smali_file.write("    " + split + " " + str(new_locals_value)) # write the new .locals into the file
                    write_input_smali_file.write(indented_code_to_inject) # write the smali code we want to inject into the file
                    
                    inject_on_next_line = False # We finished injecting, we don't need to look for .locals anymore
                    injection_successfull = True # The injection was successful
                    continue

            write_input_smali_file.write(line)
        
        # Print message based on the injection status, if it failed print an error message and kill execution
        if(injection_successfull):
            print("[+] Finished injecting smali code [+]")
        else:
            print("[!] Manual injection failed, are you sure you specified the correct arguments? [!]")
            utilities.quit()
    else:

        # Automatic injection

        global activity_name
        
        detect_decompiled_directory()

        # Get the Smali File from the 
        main_activity_name = str(activity_name.split('.')[-1])

        activity_name_list = activity_name.split('.')[:-1]
        activity_name_path = "/".join(activity_name_list)

        # Search for all the folders within the decompiled_directory that have 'smali' in their name.
        # Append them to a list
        smali_folders = []
        for root, dirs, files in walk(apktool_interface.decompiled_directory, topdown=False):
            for name in dirs:
                if('smali' in name):
                    smali_folders.append(path.join(root, name))
        
        # We also append this other name, as it's common and might contain the smali file we're looking for.
        smali_folders.append('unknown')
    
        # List that holds the statuses of our injections
        injection_successfull = []


        # For each path found in the decompiled_directory
        for temp_path in smali_folders:

            # Current path to use holding the Smali Files
            smali_path = path.join(apktool_interface.decompiled_directory, temp_path, str(path.normpath(activity_name_path)))

            # Search for smali files inside the current smali_path having the name equal to the Main Activity we found before
            print("[+] Searching "+str(main_activity_name + '*') + " in ==> "+ smali_path + " [+]")
            smali_files_available = utilities.find_file_by_pattern(main_activity_name+"*", smali_path) # Can return: Activity1.smali, Activity1$1.smali , ...

            # No file has been found
            if(len(smali_files_available) == 0):
                continue
            
            # The smali file has been found within the smali_path.
            else:

                # List that holds the paths of the smali file containing any of the onCreate() methods
                smali_path_with_oncreate = []
                for smali_path in smali_files_available:
                    smali_path_with_oncreate.append(utilities.find_string_in_file(".method protected onCreate", smali_path))
                    smali_path_with_oncreate.append(utilities.find_string_in_file(".method public onCreate", smali_path))
                    smali_path_with_oncreate.append(utilities.find_string_in_file(".method public final onCreate", smali_path)) # Found in complex apps such as Spotify

                # Filter the list to be sure there is no "empty" element
                smali_path_with_oncreate = list(filter(None, smali_path_with_oncreate))

                # Inject the smali code we read from the user-provided file into the found file(s).


                # Read the custom smali code we should inject and indent it
                input_smali_filestream = open(arg_parser.args.smali)
                code_to_inject = input_smali_filestream.readlines()
                indented_code_to_inject = utilities.indent_smali_code(code_to_inject)

                # For each smali_path having the onCreate method to inject
                for smali_path in smali_path_with_oncreate:
                    
                    # Remove strange characters from the for loop variable if there's any
                    char_to_remove = ["'", "[", "]"]
                    for character in char_to_remove:    smali_path = str(smali_path).replace(character, '')  
            
                    # Read all the lines from the original smali file and then open stream with write permissions.
                    # All the previous content will be overridden.
                    read_input_smali_file = open(smali_path, 'r').readlines()
                    write_input_smali_file = open(smali_path, 'w')

                    # Is the smali method found?
                    inject_on_next_line = False

                    for line in read_input_smali_file: # for each line
                       
                        # are the onCreate methods on the current line
                        if( ('.method protected onCreate' in line) or ('.method public onCreate' in line) or ('method public final onCreate' in line) ) :
                            inject_on_next_line = True # we will inject our custom smali code next
                       
                        if(inject_on_next_line == True ): #if we are under the correct smali method
                            if('.locals' in line): # we will inject our smali code after the .locals variable
                                split, current_locals_value = line.split() # get the current .locals values in two separate variables
                            
                                # .locals values must be a value between 0 and 15 
                                if(current_locals_value == 15): continue
                                # else increase it to be sure our smali code will work 
                                else:
                                    new_locals_value = int(current_locals_value) + 1 # increase

                                write_input_smali_file.write("    " + split + " " + str(new_locals_value)) # write the new .locals into the file
                                write_input_smali_file.write(indented_code_to_inject) # write the smali code we want to inject into the file
                                print("[+] Injected Smali Code into " + path.basename(smali_path) + " [+]")
                                inject_on_next_line = False # We finished injecting, we don't need to look for .locals anymore in this file
                                injection_successfull.append('True') # The injection was successful, append it to our list
                                continue

                        write_input_smali_file.write(line)
            
        # Success if our list of statuses is greater than 0 and all of them are True, else print an error message and kill execution
        if( len(injection_successfull) > 0 and all(injection_successfull) ):
            print("[+] Finished injecting smali code [+]")
        else:
            print("[!] Automatic injection didn't work, please try manual injection using the --smali-file and --smali-method arguments [!]")
            utilities.quit()