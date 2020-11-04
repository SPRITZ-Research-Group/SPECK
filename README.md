# SPECK: From Google Textual Guidelines to Automatic Detection of Android Apps Vulnerabilities

SPECK is a tool designed to search for several bad coding pratices on an Android application, either in source code or packaged APKs. From the [android documentation](https://developer.android.com/topic/security/best-practices), we extracted a set of rules to follow, in order to preserve apps' security. It performs a static analysis by looking through the source code of an app, in order to detect rules' violations.

Three levels of severity in terms of security are distinguished:

* *INFO* 		: a good coding practice detected
* *WARNING*	: a security issue presumed, for information
* *CRITICAL*	: a security issue confirmed



## Configuration

Run the following commands to configure SPECK:

```
sed -i -e 's/\r$//' ./server/apk2src/jadx/gradlew
sed -i -e 's/\r$//' ./server/apk2src/decompiler.sh
./server/apk2src/jadx/gradlew dist -p ./server/apk2src/jadx/
```



## Usage

This tool can be run in two different modes: the developer mode and the user mode.

### *developer_mode*

To analyse a single app, go to the `server/` directory and run:

```
python3 Scan.py -s SOURCE [-r RULES [RULES ...]] [-t TIMEOUT] [-g] [-q] [-D DATABASE]
```

where:

* `-s` : source code or apk path (*required*)
* `-r` : rules to be used for the analysis
* `-t` : set a timeout value
* `-g` : display good practices
* `-q` : quiet mode
* `-D` : specify the name of a *MongoDB* database where to store the analysis results; data is stored in the following two collections:
	* *rawoutput*: it contains the raw output from the analysis. This is for precision (true/false positive) plots.
	* *rulestats*: it contains the time spent for each run and for each APK. This is used for performances evaluation.




### *user_mode*

The user mode consists of two parts: the server and the app. The *server* receives the analysis requests by the *app*. It analyses the requested application and then sends back to the app its report. The user can choose if sending directly the APK from the device to the server, or let the server to download the APK from [apkpure.com](https://apkpure.com/). 

#### Run Server
To start the server, go to the `server/` directory and run:

```
python3 Server.py -i <IP> -p <PORT> -t <TIMEOUT>
```

When parameters are not specified, the following default values are used:

* IP: 127.0.0.1
* PORT: 8888
* TIMEOUT 10000

#### SPECK app

The app's source code can be found in the `speck/` directory.

When open, the SPECK app shows the list of all the third-party applications on the device. Just tapping one of them makes the app connecting to the server, in order to perform the analysis. Once the analysis is completed, tapping again on the analysed app allows to read its analysis report.

The app's default settings are:

* For server connection:
	* IP: 10.0.2.2 (useful when using an emulator and running the server on the same machine)
	* port: 8888
* The APK is sent directly from the device to the server. 

These default behaviours can be changed in the app from the *settings*.

# Video Demo

For a quick overview, you can find two short videos under: SPECK/demo/

## Rules Documentation

The formalised rules enforced in SPECK are the followings:

**PART 1: https://developer.android.com/topic/security/best-practices**

- Rule1     : Show an App Chooser
- Rule2     : Control Access to yours Content Providers
- Rule3     : Provide the right permissions
- Rule4     : Use intents to defer permissions
- Rule5     : Use SSL Traffic
- Rule6     : Use HTML message channels
- Rule7     : Use WebView objects carefully
- Rule8     : Store private data within internal storage
- Rule9     : Share data securely across apps
- Rule10    : Use scoped directory access
- Rule11    : Store only non-sensitive data in cache files
- Rule12    : Use SharedPreferences in private mode
- Rule13    : Keep services and dependencies up-to-date
- Rule14    : Check validity of data

**PART 2: https://developer.android.com/training/articles/security-tips**

- Rule15    : Avoid custom dangerous permission
- Rule16    : Erase data in webview cache
- Rule17    : Avoid SQL injections
- Rule18    : Prefer explicit intents
- Rule19    : Use IP Networking
- Rule20	  : Use services
- Rule21    : Use telephony networking
- Rule22    : Use cryptography
- Rule23    : Use broadcast receivers
- Rule24    : Dynamically load code

**PART 3: https://developer.android.com/training/articles/security-ssl**

- Rule25    : Hostname verification
- Rule26    : SSLSocket

**PART 4: https://developer.android.com/training/articles/security-config**

- Rule27    : Configure CAs for debugging
- Rule28    : Opt out of cleartext traffic

**PART 5: https://developer.android.com/guide/topics/security/cryptography**

- Rule29    : Choose a recommended algorithm
- Rule30    : Deprecated cryptographic functionality

**PART 6: https://developer.android.com/training/articles/direct-boot**

- Rule31    : Migrate existing data
- Rule32    : Access device encrypted storage
