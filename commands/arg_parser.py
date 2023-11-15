# arg_parser.py
# =====================================================
# This module is used to detect the arguments provided
# =====================================================

from argparse import ArgumentTypeError
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from sys import exit
from sys import argv
from sys import stderr
from textwrap import dedent
from os import path

def file_path(path_to_check):
    """
    file_path() checks if a path does exist or not.
    In case it does not, raise an ArgumentTypeError.

    :path_to_check: the path you want to check.
    """
    if path.exists(path_to_check):
        return path_to_check
    else:
        raise ArgumentTypeError(f"file doesn't seem to exist.")

# Gets added at the end of -h , --help
custom_epilog=dedent("""
        Examples:
        
        # Install all the requirements and install latest version of apktool
        > smali-baker.py --setup-requirements --setup-apktool
                     
        # Only create a new keystore
        > smali-baker.py --setup-certificate
                     
        # Do all the --setup options at once 
        > smali-baker.py --setup-requirements --setup-apktool --setup-certificate
        
        # Inject code from custom_smali.txt inside your apk, then zipalign and resign it. [AUTOMODE]
        > smali-baker.py --apk apkname.apk --smali custom_smali.txt --cert-path baker.keystore --cert-pass smalibaker --cert-alias baker
                     
        # Inject code from custom_smali.txt inside a specific Smali File and method, then zipalign and resign it.
        > smali-baker.py --smali custom_smali.txt --decompiled-path DECOMPILED/decompiled-apk --smali-file DECOMPILED/decompiled-apk/smali/com/../*.smali \\
        --smali-method ".method public constructor" --cert-path baker.keystore --cert-pass smalibaker --cert-alias baker

        
        Support on GitHub if you like the project! :)
""")

# Arguments that can be accepted, will be used to build -h , --help 
parser = ArgumentParser(prog="smali-baker", description="Toast Messages / Dialogs Injection made easy.", epilog=custom_epilog, formatter_class=RawDescriptionHelpFormatter)
parser.add_argument("--setup-requirements", help="Install jarsigner and zipalign.", action='store_true')
parser.add_argument("--setup-apktool", help="Install latest version of apktool.", action='store_true')
parser.add_argument("--setup-certificate", help="Create a new certificate to sign the APK.", action='store_true')
parser.add_argument("--apk", help="Path to the targeted APK file.", type=file_path,metavar='')
parser.add_argument("--smali", help="Path to the file containing Smali code to inject.", type=file_path,metavar='')
parser.add_argument("--decompiled-path", help="[OPTIONAL] Path to the decompiled APK ",metavar='')
parser.add_argument("--smali-file", help="[OPTIONAL] Inject the smali code directly into a specific Smali file.", type=file_path, metavar='')
parser.add_argument("--smali-method", help="[OPTIONAL] Inject the smali code directly into a specific method.", metavar='')
parser.add_argument("--cert-path", help="Path to keystore.", type=file_path,metavar='')
parser.add_argument("--cert-pass", help="Password of keystore.", metavar='')
parser.add_argument("--cert-alias", help="Alias of keystore.", metavar='')

# If no arguments has been provided, print -h
if len(argv)==1:
    parser.print_help(stderr)
    exit(1)

# Parse all the arguments specified by the user
args = parser.parse_args()


# If any of the setup commands is set, the user should not specify any other option
if( (args.setup_requirements == True) or (args.setup_apktool == True) or (args.setup_certificate == True) ): # Any of the setup arguments specified
    # If any other argument has been specified
    if( (args.apk is not None) or (args.smali is not None) or (args.cert_path is not None) or (args.cert_pass is not None) or (args.cert_alias is not None) or 
       (args.smali_file is not None) or (args.smali_method is not None) or (args.decompiled_path is not None)):
            # Raise a parser error, here we could also suppress traceback with
            # sys.tracebacklimit = 0
            raise parser.error("please don't specify any other arguments other than the --setup-* ones if you are trying to install dependencies.")
    
# If any of the 'manual injection' arguments is set, the user should not specify the --apk option
elif ( (args.decompiled_path is not None) or (args.smali_file is not None) or (args.smali_method is not None) ):
     if( (args.apk is not None) ): # User shouldn't provide an --apk in manual mode
        # Raise a parser error
        raise parser.error("manual injection detected with invalid arguments. Don't specify --apk if you are targeting a --smali-file.")     
     
    # List of all the arguments needed for manual injection to work
     manual_method_args = [args.smali, args.decompiled_path, args.smali_file, args.smali_method, args.cert_path, args.cert_pass, args.cert_alias]

    # If all the required arguments available in the manual_method_args are set, all the arguments are ready
     if (all(manual_method_args) ):
          arguments_ready = True
    
    # Else, check which argument from our list is missing and append it to a new list and then print it in a parser error.
     else:
          missing_arguments = []
          if ( args.decompiled_path is None ): missing_arguments.append('--decompiled-path')
          if ( args.smali is None): missing_arguments.append('--smali')
          if ( args.smali_file is None): missing_arguments.append('--smali-file')
          if ( args.smali_method is None): missing_arguments.append('--smali-method')
          if ( args.cert_path is None): missing_arguments.append('--cert-path')
          if ( args.cert_pass is None): missing_arguments.append('--cert-pass')
          if ( args.cert_alias is None): missing_arguments.append('--cert-alias')
          # Raise a parser error
          raise parser.error("manual injection detected with missing arguments.\nCurrently missing: "+str(', '.join(missing_arguments)))   


          
# If any of the arguments required is missing, append them to a new list and then print it in a parser error.
elif ( (args.apk is None) or (args.smali is None) or (args.cert_path is None) or (args.cert_pass is None) or (args.cert_alias is None) ):
     missing_arguments = []
     if( args.apk is None ): missing_arguments.append("--apk")
     if( args.smali is None ): missing_arguments.append("--smali")
     if( args.cert_path is None ): missing_arguments.append("--cert-path")
     if( args.cert_pass is None ): missing_arguments.append("--cert-pass")
     if( args.cert_alias is None ): missing_arguments.append("--cert-alias")
     
     # Raise a parser error
     raise parser.error("please, specify all the required arguments.\nCurrently missing: "+str(', '.join(missing_arguments)))
else:
     
     # All the arguments are ready
     arguments_ready = True
