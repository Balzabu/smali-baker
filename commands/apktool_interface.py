# apktool_interface.py
# =====================================================
# This module is used to decompile the APK provided by
# arg_parser.py
# =====================================================

from commands import utilities
from commands import arg_parser
from subprocess import check_call
from subprocess import CalledProcessError
from os import devnull
from os import path
from time import sleep
from threading import Thread

global has_been_decompiled
global stop_animation
global decompiled_directory

stop_animation = False

def show_animation(type):
    """
    show_animation() prints a loading animation on screen while other tasks are running.

    :type: can be "decompile" or "compile" in order to change the message that gets displayed with the animation.
    """
    global stop_animation
    
    animation = [
        "{        }",
        "{=       }",
        "{===     }",
        "{====    }",
        "{=====   }",
        "{======  }",
        "{======= }",
        "{========}",
        "{ =======}",
        "{  ======}",
        "{   =====}",
        "{    ====}",
        "{     ===}",
        "{      ==}",
        "{       =}"
    ]

    for status in animation:
        if(stop_animation == True):
            break
        else:
            # Override previous line, we can also use this other method:
            #status_message = "[+] Decompiling APK " + status + " [+]"
            #sys.stdout.write('\r'+status_message)
            if(type == "decompile" or type == "Decompile"): print("[+] Decompiling APK " + status + " [+]", end="\r")
            elif(type == "compile" or type == "Compile"): print("[+] Compiling APK " + status + " [+]", end="\r")
            sleep(0.1)

def apktool_decompile():
    """
    apktool_decompile() decompiles the specified APK using apktool.
    Kills execution in case of errors.
    """
    global has_been_decompiled
    global stop_animation
    global decompiled_directory

    script_directory = utilities.get_script_directory()
    decompiled_files_folder = "DECOMPILED"
    apk_name = path.splitext(path.basename(arg_parser.args.apk))[0]
    apk_name = apk_name + "-" + str(int(utilities.unix_timestamp()))
    decompiled_directory = path.join(script_directory, decompiled_files_folder, apk_name) # $SCRIPT_FOLDER/DECOMPILED/$APK_NAME-$UNIX_TIMESTAMP

    try:
        check_call(['apktool', 'd', arg_parser.args.apk, '-o', str(decompiled_directory)], stdout=open(devnull,'wb'), stderr=open(devnull,'wb'))
        has_been_decompiled = True
    except CalledProcessError as e:
        print("[!] There was an error while decompiling the APK [!]")
        print("[!] Traceback: return with exit status {} => {}".format(e.returncode, e.output) + " [+]")
        print("[+] Please try to run the 'apktool d "+ arg_parser.args.apk + "' command manually for more informations [+]")
        has_been_decompiled = False
        stop_animation = True

def decompile_apk():
    """
    decompile_apk() creates a new Thread for the apktool_decompile() function.
    While the thread is alive, the animation function show_animation() is called.
    Kills execution in case of errors.
    """
    
    global has_been_decompiled
    global decompiled_directory

    decompile_process = Thread(name='decompile', target=apktool_decompile)
    decompile_process.start()

    while decompile_process.is_alive():
        show_animation("decompile")
    else:
        if(has_been_decompiled == True):
            print("[+] APK decompiled successfully => " + decompiled_directory + " [+]")
        elif(has_been_decompiled == False):
            print("[!] Couldn't decompile the APK [!]")
            utilities.quit()
        else:
            print("[!] Unexpected error while decompiling the APK [!]")
            utilities.quit()



def apktool_build():
    """
    apktool_build() compiles the specified APK using apktool.
    Kills execution in case of errors.
    """
    global has_been_compiled
    global stop_animation
    global decompiled_directory

    try:
        check_call(['apktool', 'b', str(decompiled_directory)], stdout=open(devnull,'wb'), stderr=open(devnull,'wb'))
        has_been_compiled = True
    except CalledProcessError as e:
        print("[!] There was an error while compiling the APK [!]")
        print("[!] Traceback: return with exit status {} => {}".format(e.returncode, e.output) + " [+]")
        print("[+] Please try to run the 'apktool b "+ str(decompiled_directory) + "' command manually for more informations [+]")
        has_been_compiled = False
        stop_animation = True


def compile_apk():
    """
    compile_apk() creates a new Thread for the apktool_build() function.
    While the thread is alive, the animation function show_animation() is called.
    Kills execution in case of errors.
    """
    global has_been_compiled
    global decompiled_directory

    expected_output_directory = path.join(decompiled_directory, "dist")

    compile_process = Thread(name='compile', target=apktool_build)
    compile_process.start()

    while compile_process.is_alive():
        show_animation("compile")
    else:
        if(has_been_compiled == True):
            print("[+] APK has been compiled successfully => " + expected_output_directory + " [+]")
        elif(has_been_compiled == False):
            print("[!] Couldn't compile the APK [!]")
            utilities.quit()
        else:
            print("[!] Unexpected error while compiling the APK [!]")
            utilities.quit()