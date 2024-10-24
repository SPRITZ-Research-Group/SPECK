# SPECK: From Google Textual Guidelines to Automatic Detection of Android Apps Vulnerabilities

This repo contains the code for our paper "SPECK: From Google Textual Guidelines to Automatic Detection of Android Apps Vulnerabilities". It includes both the code of our tool,
SPECK, as well as the code of IVA, an Intentionally Vulnerable App used in our
evaluation.

## SPECK

SPECK is a tool designed to search for several bad coding pratices on an Android application. From the [android documentation](https://developer.android.com/topic/security/best-practices), we extracted a set of rules to follow, in order to improve apps' security. It performs a static analysis by looking through the source code of an app, in order to detect rules' violations.

Three levels of severity in terms of security are distinguished:

-   _INFO_ : a good coding practice detected
-   _WARNING_ : a security issue presumed, for information
-   _CRITICAL_ : a security issue confirmed

### Demo First!

A quick overview of the tool can be found in this short [video](https://github.com/SPRITZ-Research-Group/SPECK/blob/main/demo/SPECK_Developer_Mode.mp4):

![Developer mode demo](./demo/developermode.gif)

### Usage

To analyse a single app, go to the `SPECK/` directory and run:

```
python3 Scan.py -s SOURCE [-r RULES [RULES ...]] [-t TIMEOUT] [-g] [-q] [-D DATABASE]
```

where:

-   `-s` : path to the source code or the apk of the app (_required_)
-   `-r` : rules to be used for the analysis
-   `-t` : set a timeout value
-   `-g` : display good practices
-   `-q` : quiet mode
-   `-D` : specify the configuration of a _MongoDB_ database where to store the analysis results; data is stored in the following two collections:
    -   _rawoutput_: it contains the raw output from the analysis. This is for precision (true/false positive) plots.
    -   _rulestats_: it contains the time spent for each run and for each APK. This is used for performances evaluation.

## Rules Documentation

The formalised rules enforced in SPECK are the followings:

**PART 1: https://developer.android.com/topic/security/best-practices**

-   Rule1 : Show an App Chooser
-   Rule2 : Control Access to yours Content Providers
-   Rule3 : Provide the right permissions
-   Rule4 : Use intents to defer permissions
-   Rule5 : Use SSL Traffic
-   Rule6 : Use HTML message channels
-   Rule7 : Use WebView objects carefully
-   Rule8 : Store private data within internal storage
-   Rule9 : Share data securely across apps
-   Rule10 : Use scoped directory access
-   Rule11 : Store only non-sensitive data in cache files
-   Rule12 : Use SharedPreferences in private mode
-   Rule13 : Check validity of data

**PART 2: https://developer.android.com/training/articles/security-tips**

-   Rule14 : Avoid custom dangerous permission
-   Rule15 : Erase data in webview cache
-   Rule16 : Avoid SQL injections
-   Rule17 : Prefer explicit intents
-   Rule18 : Use IP Networking
-   Rule19 : Use services
-   Rule20 : Use telephony networking
-   Rule21 : Use cryptography
-   Rule22 : Use broadcast receivers
-   Rule23 : Dynamically load code

**PART 3: https://developer.android.com/training/articles/security-ssl**

-   Rule24 : Hostname verification
-   Rule25 : SSLSocket

**PART 4: https://developer.android.com/training/articles/security-config**

-   Rule26 : Configure CAs for debugging
-   Rule27 : Opt out of cleartext traffic

**PART 5: https://developer.android.com/guide/topics/security/cryptography**

-   Rule28 : Choose a recommended algorithm
-   Rule29 : Deprecated cryptographic functionality

**PART 6: https://developer.android.com/training/articles/direct-boot**

-   Rule30 : Migrate existing data
-   Rule31 : Access device encrypted storage

## Intentionally Vulnerable App (IVA)

In the `VulnerableApp` folder we included the code for IVA, an Intentionally
Vulnerable App we developed to evaluate how good tools are at reporting violations
of the Google Textual Guidelines. We developed IVA with the following requirements
in mind:

1. **It should violate all the Google Textual guidelines**: we want to know what
   violations are detected by analysis tools.
2. **It should not include external code**: We don't want to risk importing external
   libraries that have additional violations, since we want to tell if a tool detects
   the violations _we inserted_.
