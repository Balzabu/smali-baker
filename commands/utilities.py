# utility.py
# ===========================================================
# This module contains a variety of functions, mostly
# used to replace code we need to execute more than one time.
# ===========================================================

from os import geteuid
from os import chmod
from os import walk
from os import path
from os import devnull
from shutil import move
from shutil import which
from sys import exit
from sys import argv
from time import sleep
from time import time
from urllib import request as urllib_request
from urllib import error as urllib_error
from subprocess import check_call
from subprocess import CalledProcessError
from platform import system
from fnmatch import fnmatch
from tqdm import tqdm

def credits():
    """
    credits() prints a cute ascii art of Chef from South Park.
    The logo is 'slowly typed' out.
    """

    ascii_art = ["",
                "⠀⠀⠀⠀⠀⠀⣀⣀⣀⣠⣴⣶⣶⡶⠾⠟⠛⠶⣦⣴⠶⣦⡀",
                "⠀⠀⠀⠀⢠⡾⠋⠉⠉⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⡇",
                "⠀⠀⠀⠀⠸⣷⣀⣀⣤⣀⣠⣦⣄⣀⣠⡶⣦⣤⣤⡾⡟⠋",
                "⠀⠀⠀⠀⠀⠈⢹⠋⠈⡍⠀⠀⠉⡍⠁⠀⠀⢠⠀⠀⡇",
                "⠀⠀⠀⠀⠀⠀⢸⠀⠀⡇⠀⢀⣀⣃⣀⣀⡀⠸⠀⠀⡇⠀⠀⠀⠀ Smali Oven",
                "⠀⠀⠀⠀⠀⠀⢸⡦⠔⢒⣿⠛⠛⢿⡟⠙⠻⣿⠛⢻⡇⠀    --------------->",
                "⠀⠀⠀⠀⠀⠀⢸⡇⠀⠈⣇⠀⢈⡼⢇⣀⢈⡟⠀⢸⡇⠀⠀⠀⠀ Created by Balzabu",
                "⠀⠀⠀⠀⠀⠀⢸⣷⠀⠀⠈⠉⠡⠄⠤⠭⠁⠀⠀⣼⡇⠀⠀⠀⠀ https://github.com/balzabu",
                "⠀⠀⠀⠀⠀⠀⣸⣿⣷⣄⣠⡖⠚⠿⠓⠒⣦⣠⣾⣿⡷⠦⣄⡀",
                "⠀⠀⠀⠀⡤⠚⠉⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠛⢁⠀⠀⠙⠳⣄",
                "           ⠈⠉⠉⠉⠉⠉⠉⠉"]

    for row in ascii_art:
        sleep(0.1)
        print(row)

def quit():
    """
    quit() exits the script, before it prints a message.
    """
    print("[+] Goodbye, remember to leave a star on GitHub! [+]")
    exit()


def running_as_root():
    """
    running_as_root() checks if the script is running with root privileges.
    Else it calls the quit() function.
    """
    if (geteuid() != 0):
        print("[!] Please run the script as root [!]")
        quit()


def get_script_directory():
    """
    get_script_directory() returns the path where the script has been launched from.
    """
    return path.dirname(path.abspath(argv[0]))


def unix_timestamp():
    """
    unix_timestamp() returns the current Unix Timestamp.
    """
    return time()

def find_file_by_pattern(pattern, path_to_search):
    """
    find_folder_by_pattern() searches for a file using a pattern.

    :pattern: is the wildcard mask we want to use
    :path_to_search: parent directory from where start searching
    :return: returns the File Paths where the pattern has been found
    """
    result = []
    for root, dirs, files in walk(path_to_search):
        for name in files:
            if fnmatch(name, pattern):
                temp_filepath = path.join(root,name)
                result.append(temp_filepath)
    return result

def find_string_in_file(string_to_search, path_to_file):
    """
    find_string_in_file() searches for a string inside a file.

    :string_to_search: the text you're trying to find within the files
    :path_to_file: the list of file paths to search into
    :return: returns the File Paths where the string has been found
    """
    result = []
    if path.isfile(path_to_file):
        filestream = open(path_to_file, 'r')
        if string_to_search in filestream.read():
            print("[+] Found onCreate method inside " + path.basename(path_to_file) + " [+]")
            result.append(path_to_file)
        filestream.close()
    return result

def indent_smali_code(lines_to_indent):
    """
    indent_smali_code() indents text, adding 4 whitespaces at the beginning of each line.
    Will also add additional lines to specify the beginning and the end of the smali patch.

    :string_to_search: the text you're trying to find within the files
    :path_to_file: the list of file paths to search into
    :return: returns the File Paths where the string has been found
    """
    index_lines = 0
    fixed_lines = ""

    for line in lines_to_indent:
        if(index_lines == 0):
            fixed_lines += "\n\n"
            fixed_lines += '    {0}'.format("# smali-baker patches begin")
            fixed_lines += "\n\n"
        
        index_lines += 1
        line = line.strip()
        fixed_lines += '    {0}\n'.format(line)

        if(index_lines == len(lines_to_indent)):
            fixed_lines += "\n"
            fixed_lines += '    {0}'.format("# smali-baker patches end")
            fixed_lines += "\n"
    
    return fixed_lines

def chmod_ax(file_path):
    """
    chmod_ax() runs the command 'chmod a+x' on a file.
    Uses os.chmod().
    """
    chmod(file_path, 0o777)


def chmod_r_ax(folder_path):
    """
    chmod_r_ax() runs the command 'chmod -R 0777' on a path.
    Runs a subprocess in order to execute the command.

    :folder_path: the folder where you want to recursively change the permissions to 0777.
    """
    try:
        check_call(['chmod', '-R', '0777', folder_path], stdout=open(devnull,'wb'), stderr=open(devnull,'wb'))
    except CalledProcessError as e:
        print("[!] There was an error while changing script folder permissions [!]")
        print("[!] Traceback: return with exit status {} => {}".format(e.returncode, e.output) + " [+]")


def move_file(origin_path,destination_path):
    """
    move_file() moves a file from a directory to another.

    :origin_path: path to the source file.
    :destination_path: path to the destination.
    """
    try:
        move(origin_path, destination_path)
    except FileNotFoundError: 
        print ('[!] The file you\'re trying to move doesn\'t exist [!]')
        quit() 
    # Add whatever logic you want to execute
    except Exception as e: 
        print("[!] Error while moving the file [!]")
        print("Exception: \n ===========")
        print(e)
        quit()


class DownloadProgressBar(tqdm):
    """
    DownloadProgressBar is a custom class used to show a progress bar while downloading a file.

    :tqdm: an instance of tqdm
    """
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)

def download_url(url, output_path):
    """
    download_url() downloads a file while also showing a progress bar using the custom DownloadProgressBar class.
    Will kill execution and print exceptions in case of errors.

    :url: url to download
    :output_path: path where to store the downloaded file
    """
    try:
        with DownloadProgressBar(unit='B', unit_scale=True,
                                miniters=1, desc=url.split('/')[-1]) as t:
            urllib_request.urlretrieve(url, filename=output_path, reporthook=t.update_to)
    # https://docs.python.org/3/library/urllib.error.html
    except urllib_error.HTTPError as e:
        print("[!] There was an error while downloading your file [!]")
        print("Exception: \n ===========")
        print(e.__dict__)
        quit()

    except urllib_error.URLError as e:
        print("[!] There was an error while downloading your file [!]")
        print("Exception: \n ===========")
        print(e.__dict__)
        quit()
    
    except Exception as e:
        print("[!] There was an error while downloading your file [!]")
        print("Exception: \n ===========")
        print(e)
        quit()

def detect_OS():
    """
    detect_OS() detects the running OS.

    :return: returns the string containing the system name ('Linux','Windows',...)
    """
    client_os = system()
    return client_os

def is_Supported(client_os):
    """
    is_Supported() checks if the provided OS is supported by the script.
    Currently only linux is supported.

    :return: bool True in case the OS is supported.
    """
    if(client_os == 'Linux'):
        return True
    else:
        return False    

def is_Command_Available(name):
    """
    is_Command_Available() checks if a command is available on the system.

    :name: the command you want to check.
    :return: returns a bool if the which() doesn't return None.
    """
    return which(name) is not None