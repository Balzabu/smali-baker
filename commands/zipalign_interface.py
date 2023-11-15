# zipalign_interface.py
# =====================================================
# This module is used to zipalign the APK built with
# apktool_interface.py
# =====================================================

from commands import utilities
from commands import arg_parser
from commands import apktool_interface
from subprocess import check_call
from subprocess import CalledProcessError
from os import path
from os import devnull

global expected_zipaligned_apk_path

def get_aligned_apk_name():
    """
    get_aligned_apk_name() returns the apk name we will use for the zipalign result.
    Uses the --apk specified argument to extract the current APK name and extension and fix it accordingly.

    :return: will return $APK_NAME-aligned.apk
    """
    source_apk_name = path.basename(arg_parser.args.apk)
    destination_apk_name, source_apk_extension = path.splitext(source_apk_name)
    destination_apk_name = str(destination_apk_name) + "-aligned" + str(source_apk_extension) # $APK_NAME-aligned.apk
    return (destination_apk_name)

def zipalign():
    """
    zipalign() zipaligns the compiled APK containing the Smali Code we injected.
    In the case of 'manual injection' we build the destination_apk_name with the arguments provided by the user, else we will call the 
    get_aligned_apk_name() function.

    """
    global expected_zipaligned_apk_path

    # manual injection
    # if --apk is not set, and --decompiled-path is set
    if( (arg_parser.args.apk is None) and (arg_parser.args.decompiled_path is not None)):
        expected_compiled_apk_path = path.join(apktool_interface.decompiled_directory, "dist")
        detect_apk_name = utilities.find_file_by_pattern('*.apk',expected_compiled_apk_path)
        if(len(detect_apk_name) < 0):
            print("[!] Couldn't find the APK to zipalign [!]")
            utilities.quit()
        if(len(detect_apk_name) > 1):
            print("[!] Zipalign failed, there are too many APK files in " + str(expected_compiled_apk_path) + " [!]")
            utilities.quit()
        else:
            expected_compiled_apk_path = path.join(detect_apk_name[0])
            #does the same as get_aligned_apk_name()
            destination_apk_name = str(path.splitext(path.basename(expected_compiled_apk_path))[0]) + "-aligned" + str(path.splitext(path.basename(expected_compiled_apk_path))[1])
            expected_zipaligned_apk_path = path.join(apktool_interface.decompiled_directory, "dist", destination_apk_name)

    # automatic mode
    # if --apk is set and --decompiled-path is not set
    elif( (arg_parser.args.apk is not None) and (arg_parser.args.decompiled_path is None) ):
        expected_compiled_apk_path = path.join(apktool_interface.decompiled_directory, "dist", path.basename(arg_parser.args.apk))
        expected_zipaligned_apk_path = path.join(apktool_interface.decompiled_directory, "dist", get_aligned_apk_name())
    
    # Execute the zipalign command
    try:
        check_call(['zipalign','-v', '4', expected_compiled_apk_path, expected_zipaligned_apk_path], stdout=open(devnull,'wb'), stderr=open(devnull,'wb'))        
    except CalledProcessError as e:
        print("[!] There was an error while zipaligning the APK [!]")
        print("Traceback: return with exit status {} => {}".format(e.returncode, e.output))
        utilities.quit()
    print("[+] APK zipaligned [+]")
