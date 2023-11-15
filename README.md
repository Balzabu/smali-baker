Smali Baker
-----

![logo](https://raw.githubusercontent.com/Balzabu/smali-baker/main/smali-baker.jpg)

<p align="center">
  <img src="https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54" height="23">
  <img src="https://img.shields.io/badge/Android-3DDC84?style=for-the-badge&logo=android&logoColor=white" height="23">
  <img src="https://img.shields.io/badge/Debian-D70A53?style=for-the-badge&logo=debian&logoColor=white" height="23">
  <img src="https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white" height="23">
</p>

### Got a question?
I'm always happy to answer questions! Here are some good places to ask them:

 - for anything you're curious about, try [noc@balzabu.io](mailto:noc@balzabu.io).
 - for general questions or to suggest bugfixes about Smali Baker open an Issue [here](https://github.com/Balzabu/smali-baker/issues)


### What is Smali Baker?

Smali Baker is a python script designed to help pentesters and modders automatically inject toast messages and dialogs into APK files.

It's partner in crime, smali-oven, is able to generate the smali code required on-the-fly through a simple website I built which is currently hosted on Github Pages.

For more informations about smali-oven refer to its [repository](https://github.com/balzabu/smali-oven).

### So... what it does?

Smali Baker is able to decompile, search within the AndroidManifest.xml file for the starting activities, and then inject the user-specified smali code into them.

It also takes care of:
 - Decompiling and recompiling the APK with apktool 
 - Zipaligning the apktool output APK
 - Signing the apktool output APK 

Works also in manual mode, thus providing the ability to inject specific smali files and methods.

It supports installation of all necessary requirements through APT.
<br>
It has been througly tested on Ubuntu 22.04 but should work just fine in all Debian-based operating systems.
<br>
Smali Baker was made to make it easily modifiable so be free to adjust it to suit your preferences.

For more information regarding how to install the dependencies, I encourage you to refer to your distribution manuals.

Currently, in order to work, smali-baker requires:

 - Java Development Kit (APT packages ==> [default-jdk](https://pkgs.org/search/?q=default-jdk) / [default-jre](https://pkgs.org/search/?q=default-jre))
 - apksigner (APT package ==> [apksigner](https://pkgs.org/search/?q=apksigner))
 - Python3 PIP modules: [TQDM](https://github.com/tqdm/tqdm), [Requests](https://github.com/psf/requests)

Note: on Windows be sure all the commands have been added to the PATH environment variable.
<br>
In case you find "uncommon" tags in the AndroidManifest which aren't currently implemented, feel free to submit a pull request.

### How is the Injection performed?
Smali Baker does what you would normally do to inject smali code into your targeted APK.


In "Automatic Mode" it reads the AndroidManifest.xml of the decompiled APK to find what's the starting activity that has an `<intent-filter>` like this:

```xml
<intent-filter>
    <action android:name="android.intent.action.MAIN" />
    <category android:name="android.intent.category.LAUNCHER" />
</intent-filter>
```

In "Manual Mode" the user can provide the exact Smali File and method to inject. 

Then, it finds the corresponding smali file and reads all the lines looking for specific methods.
Once one of them has been found, it then searches for the ".locals" variable in order to take note of its current value; if the current value is less than 15, it gets incremented and our code is injected. (For more informations about why .locals can't usually be higher than 15 can be found [here](http://pallergabor.uw.hu/androidblog/dalvik_opcodes.html)).
<br> 
Following the changes, the file will have it's original lines intact with our new code injected and indented.

In case you want to edit the code to implement your own injection method, you can edit the "injector.py" module.

### Why?
The project started when I had the idea of automating the injection of Toast Messages into modded APKs since, when injecting them manually, there are many boring operations that need to be performed (Think about zipaligning and resigning the APK each time).

### Installation
 - Clone this repository
    ```bash
    git clone https://github.com/Balzabu/smali-baker
    ```
 - Cd into the directory
    ```bash
    cd smali-baker
    ```
 - Execute the script as root with the --setup arguments
    ```bash
    sudo python3 smali-baker.py --setup-requirements --setup-apktool --setup-certificate
    ```

### Usage

Please refer to the --help argument output for usage examples.

### Arguments
| Command                                     | Description                                                                                                 |
| ------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| \--help                                     | Shows a list of the commands available through argparser and provides example on how to use the script.<br> |
| \--setup--requirements                      | Installs the main requirements for the script to work, such as: jarsigner, zipalign and apksigner.          |
| \--setup--apktool                           | Installs the latest version of apktool through GitHub.                                                      |
| \--apk {path_to_apk_file}                   | Used to specify the APK you want to inject into.                                                            |
| \--smali {path_to_smali_file}               | Used to specify the file containing the Smali Code you want to inject.                                      |
| \--decompiled-path {path_to_folder}         | [MANUAL INJECTION] Used to specify the path containing the Decompiled APK                                   |
| \--smali-file {path_to_file}                | [MANUAL INJECTION] Used to specify the Smali File you want to inject.                                       |
| \--smali-method                             | [MANUAL INJECTION] Used to specify the Smali Method, within the targeted Smali File, you want to inject.    |
| \--path-certificate {path_to_certificate}   | Used to specify the path to the keystore we will use to sign the injected APK.                              |
| \--cert-password {password_for_certificate} | Used to specify the password for the keystore.                                                              |
| \--cert-alias {alias_certificate}           | Used to specify the alias for the keystore.                                                                 |
