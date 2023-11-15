# apksigner_interface.py
# ============================================================
# This module is used to sign the APK built with
# apktool_interface.py, zipaligned with zipalign_interface.py
# with the certificate provided by arg_parser.py
# ============================================================

from commands import utilities
from commands import arg_parser
from commands import zipalign_interface
from subprocess import check_call
from subprocess import CalledProcessError
from os import devnull

def sign_apk():
    """
    sign_apk() signs the compiled APK.
    The arguments for the command are provided by arg_parser and zipalign_interface.
    Signing needs to be done after zipaligning the APK if we use apksigner.
    Prints exceptions and kills execution in case of errors.
    """
    try:
        check_call(['apksigner', 'sign',
                    '--ks-key-alias', arg_parser.args.cert_alias, 
                    '--ks', arg_parser.args.cert_path,
                    '--ks-pass', str("pass:" + arg_parser.args.cert_pass),
                    zipalign_interface.expected_zipaligned_apk_path], stdout=open(devnull,'wb'), stderr=open(devnull,'wb'))        
    except CalledProcessError as e:
        print("[!] There was an error while signing the APK [!]")
        print("Traceback: return with exit status {} => {}".format(e.returncode, e.output))
        utilities.quit()
    print("[+] APK signed [+]")
