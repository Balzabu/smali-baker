# setup_commands.py
# =====================================================
# This module contains all the functions needed to
# install the requirements to make sure Smali Oven works. 
# =====================================================

from commands import utilities
from subprocess import run as run_command
from subprocess import check_output
from subprocess import check_call
from subprocess import STDOUT
from subprocess import PIPE
from subprocess import CalledProcessError
from re import search
from os import path
from os import devnull
from requests import get as requests_get

def detect_apktool_version():
    """
    detect_apktool_version() detects the latest version of APKTool available on GitHub.
    
    :return: version number without the leading "v.".
    """
    github_api_link = "https://api.github.com/repos/iBotPeaches/Apktool/releases/latest"
    
    try:
        github_response = requests_get(github_api_link)
    except:
        print("[!] Couldn't check latest version available of apktool. [!]")
        utilities.quit()
    
    json_github_response = github_response.json()
    latest_apktool_version = str(json_github_response['name']).replace('v','')
    return latest_apktool_version


def install_apktool():
    """
    install_apktool() installs APKTool automatically, doesn't use APT as it would install the 2.5.0 version.
    Kills execution and print exceptions in case of errors.
    """
    try:
        # Detect latest version number
        latest_apktool_version = detect_apktool_version()
        apktool_github_link = "https://github.com/iBotPeaches/Apktool/releases/download/v"+ latest_apktool_version + "/apktool_" + latest_apktool_version + ".jar"

        # Download the linux wrapper into /tmp
        print("[+] Downloading apktool linux wrapper [+]")
        utilities.download_url("https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool","/tmp/apktool")

        # Download latest version of apktol from the official GitHub repo
        print("[+] Downloading apktool "+ latest_apktool_version +" [+]")
        utilities.download_url(apktool_github_link, "/tmp/apktool.jar")
    except Exception as e:
        utilities.print("Exception: \n ===========")
        print(e.__dict__)
        quit()

    utilities.chmod_ax("/tmp/apktool")
    utilities.chmod_ax("/tmp/apktool.jar")

    utilities.move_file("/tmp/apktool", "/usr/local/bin/apktool")
    utilities.move_file("/tmp/apktool.jar", "/usr/local/bin/apktool.jar")
    
    print("[+] apktool v" + latest_apktool_version + " installed [+]")



def install_java_jdk():
    """
    install_java_jdk() installs 'default-jdk' and 'default-jre' into the system through APT.
    Kills execution and print exceptions in case of errors.
    """
    try:
        check_call(['apt', 'install', '-y', 'default-jdk', 'default-jre'], stdout=open(devnull,'wb'), stderr=open(devnull,'wb'))
    except CalledProcessError as e:
        print("[!] There was an error while downloading default-jdk and default-jre [!]")
        print("Traceback: return with exit status {} => {}".format(e.returncode, e.output))
        utilities.quit()
    print("[+] Packages default-jdk and default-jre installed successfully [+]")


def detect_java_sdk():
    """
    detect_java_sdk() check if Java is already installed.
    If java does result to be already installed, print a message
    on screen; otherwise, call the install_java_jdk() function to
    perform the installation automatically.
    """
    is_java_available = utilities.is_Command_Available("java")
    is_jarsigner_available = utilities.is_Command_Available("jarsigner")
    is_keytool_available = utilities.is_Command_Available("keytool")

    if(is_java_available == True and is_jarsigner_available == True and is_keytool_available == True):
        current_java_version = str(check_output(['java' , '-version'], stderr=STDOUT))
        pattern_regex_version = '\"(\d+\.\d+\.\d+).*\"'
        current_java_version = search(pattern_regex_version, current_java_version).groups()[0]
        print("[+] java is already installed; detected version => " + current_java_version + " [+]")
    else:
        install_java_jdk()


def install_zipalign():
    """
    install_zipalign() installs zipalign through APT.
    Kills execution and print exceptions in case of errors.
    """
    try:
        check_call(['apt', 'install', '-y', 'zipalign'], stdout=open(devnull,'wb'), stderr=open(devnull,'wb'))
    except CalledProcessError as e:
        print("[!] There was an error while downloading zipalign [!]")
        print("Traceback: return with exit status {} => {}".format(e.returncode, e.output))
        utilities.quit()
    print("[+] zipalign installed [+]")


def detect_zipalign():
    """
    detect_zipalign() check if zipalign is already installed.
    If zipalign does result to be already installed, print a message
    on screen; otherwise, call the install_zipalign() function to
    perform the installation automatically.
    """
    is_zipalign_available = utilities.is_Command_Available("zipalign")
    
    if(is_zipalign_available == True):
        print("[+] zipalign is already installed [+]")
    else:
        install_zipalign()


def install_apksigner():
    """
    install_apksigner() installs 'apksigner' into the system through APT.
    Kills execution and print exceptions in case of errors.
    """
    try:
        check_call(['apt', 'install', '-y', 'apksigner'], stdout=open(devnull,'wb'), stderr=open(devnull,'wb'))
    except CalledProcessError as e:
        print("[!] There was an error while downloading apksigner [!]")
        print("Traceback: return with exit status {} => {}".format(e.returncode, e.output))
        utilities.quit()
    print("[+] apksigner installed successfully [+]")

def detect_apksigner():
    """
    detect_apksigner() checks if apksigner is already installed.
    If zipalign does result to be already installed, print a message
    on screen stating it's version; otherwise, call the install_zipalign()
    function to perform the installation automatically.
    """
    # Is the command available?
    if(utilities.is_Command_Available("apksigner") == True):
        current_apksigner_version = str(run_command(['apksigner' , '--version'], stdout=PIPE).stdout.decode('utf-8').strip())
        print("[+] apksigner is already installed; detected version => " + current_apksigner_version +" [+]")
    else:
        # Else install the latest version of apksigner through APT  
        install_apksigner()

def install_requirements():
    """
    install_requirements() calls the functions detect_zipalign() and detect_java_sdk()
    which will install the requirements automatically in case they are missing.
    """
    detect_zipalign()
    detect_java_sdk()
    detect_apksigner()

def detect_certificate():
    """
    detect_certificate() check if the script directory contains the
    'baker.keystore' file used to sign the APK.
    If the certificate does result to be existing, print a message
    on screen; otherwise, call the create_certificate() function
    to create it automatically.
    """
    script_directory = utilities.get_script_directory()
    keystore_name = "baker.keystore"
    keystore_path = path.join(script_directory, keystore_name)
    if path.exists(keystore_path):
        print("[+] Detected baker.keystore inside the script directory [+]")
    else:
        create_certificate()


def create_certificate():
    """
    create_certificate() creates a keystore who will be used to 
    sign the APKs later.
    Kills execution and print exceptions in case of errors.
    """
    try:
        check_call(['keytool', '-genkey', '-keystore', 'baker.keystore', '-keyalg', 'RSA', '-keysize', '2048', '-validity', '10000', 
                    '-alias', 'baker', '-dname', 'cn=Unknown, ou=Unknown, o=Unknown, c=Unknown', '-storepass', 'smalibaker', '-keypass',
                    'smalibaker'], stdout=open(devnull,'wb'), stderr=open(devnull,'wb'))        
    except CalledProcessError as e:
        print("[!] There was an error while creating the certificate with keytool [!]")
        print("Traceback: return with exit status {} => {}".format(e.returncode, e.output))
        utilities.quit()
    print("[+] baker.keystore created with password: smalibaker , alias: baker [+]")

