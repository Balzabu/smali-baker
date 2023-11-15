# smali-baker.py
# =======================================================
# Made by Balzabu
# https://github.com/balzabu
# https://balzabu.io
# =======================================================
# This is the hearth of the whole bakery.
# Here we call our modules to do all the heavy lifting.
# Note that smali-baker, even if run on Manual Injection,
# will always try to inject under the .locals variable
# of the specified method.
# Edit the code accordingly to your needs in case you
# want to inject in other parts / under other strings.
# =======================================================

from commands import arg_parser
from commands import setup_commands
from commands import utilities
from commands import apktool_interface
from commands import injector
from commands import zipalign_interface
from commands import apksigner_interface
from subprocess import run as run_command
from subprocess import PIPE

# Main function
def main():

    # Check if running as root, else kill execution
    utilities.running_as_root()

    # Check if the detected OS is supported
    client_os = utilities.detect_OS()
    supported = utilities.is_Supported(client_os)
    
    # If it's not, print a message and kill execution
    if(supported == False):
        print("[!] Sorry, but your O.S. is currently not supported [!]")
        quit()
    
    # If --setup-requirements , --setup-apktool or --setup-certificate arguments have been specified
    if(arg_parser.args.setup_requirements == True or arg_parser.args.setup_apktool == True or arg_parser.args.setup_certificate == True):
        
        # --setup-requirements
        if(arg_parser.args.setup_requirements == True):
            
            # Check if APT is available, else kil execution
            if(utilities.is_Command_Available("apt") == False):
                print("[!] Sorry, but the script only supports APT [!]")
                quit()
            else:
                # If APT is available, proceed to install the requirements through it
                setup_commands.install_requirements()
        
        # --setup-apktool
        if(arg_parser.args.setup_apktool == True):

            # Check if apktool is already instaled, print version in case it does
            if(utilities.is_Command_Available("apktool") == True):
                current_apktool_version = str(run_command(['apktool' , '--version'], stdout=PIPE).stdout.decode('utf-8').strip())
                print("[+] apktool is already installed; detected version => " + current_apktool_version +" [+]")
            else:
                # Else install the latest version apktool available on GitHub 
                setup_commands.install_apktool()

        # --setup-certificate
        if(arg_parser.args.setup_certificate == True):

            # Check if keytool is already installed (Comes bundled in java-sdk/jre)
            if(utilities.is_Command_Available("keytool") == False):
                print("[!] Command keytool doesn't seem to exist, please install all the requirements [!]")
                quit()
            else:
                # Detect if the default baker keystore already exists, else create it and print on screen the alias and password.
                setup_commands.detect_certificate()
        print("[+] Finished performing --setup tasks [+]")

    # No --setup-* arguments have been provided, all the others are correctly set and checked from arg_parser.py
    elif(arg_parser.arguments_ready):
        utilities.credits() # print cute credits

        # If --decompiled-path, --smali-file or --smali-method has been specified, we're doing a Manual Injection
        if( ((arg_parser.args.decompiled_path is not None)) and (arg_parser.args.smali_file is not None) and (arg_parser.args.smali_method is not None)):
            apktool_interface.decompiled_directory = arg_parser.args.decompiled_path
            utilities.chmod_r_ax(utilities.get_script_directory()) # required as the script is running as root
            injector.injectSmali()
            apktool_interface.compile_apk()
            zipalign_interface.zipalign()
            apksigner_interface.sign_apk()
            utilities.chmod_r_ax(utilities.get_script_directory()) # required as the script is running as root
        
        # Else we're in automatic mode
        else:
            apktool_interface.decompile_apk()
            utilities.chmod_r_ax(utilities.get_script_directory()) # required as the script is running as root
            injector.read_AndroidManifest()
            injector.injectSmali()
            apktool_interface.compile_apk()
            zipalign_interface.zipalign()
            apksigner_interface.sign_apk()
            utilities.chmod_r_ax(utilities.get_script_directory()) # required as the script is running as root


# Run the main() function
if __name__ == '__main__':
    main()