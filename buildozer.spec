[app]

# (str) Title of your application
title = ECG App

# (str) Package name
package.name = ecgapp

# (str) Package domain (needed for android/ios packaging)
package.domain = org.yangying

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas,ttf,csv

# (list) List of inclusions using pattern matching
source.include_patterns = assets/*,images/*,fonts/*

# (list) Source files to exclude
source.exclude_exts = spec

# (list) List of directory to exclude
source.exclude_dirs = tests, bin, venv, .git, __pycache__

# (list) List of exclusions using pattern matching
source.exclude_patterns = *.pyc,*.pyo,*.git/*

# (str) Application versioning
version = 1.0

# (list) Application requirements
requirements = python3,kivy,numpy,pyjnius,pyserial

# (str) Custom source folders for requirements
# requirements.source.kivy = ../../kivy

# (list) Garden requirements
# garden_requirements =

# (str) Presplash of the application
# presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
# icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (string) Presplash background color (for android toolchain)
# Supported formats are: #RRGGBB #AARRGGBB or one of the following names:
# red, blue, green, black, white, gray, cyan, magenta, yellow, lightgray,
# darkgray, grey, lightgrey, darkgrey, aqua, fuchsia, lime, maroon, navy,
# olive, purple, silver, teal.
# android.presplash_color = #FFFFFF

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
android.fullscreen = 0

# (string) The name of the Android entry point, default is ok for Kivy apps
android.entrypoint = org.kivy.android.PythonActivity

# (string) Presplash filename for android
# android.presplash = %(source.dir)s/data/presplash.png

# (string) Icon filename for android
# android.icon = %(source.dir)s/data/icon.png

# (list) Permissions
android.permissions = BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_CONNECT,BLUETOOTH_SCAN,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# (int) Android API to use
android.api = 31

# (int) Minimum API required
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 31

# (str) Android NDK version
android.ndk = 25b

# (int) Android NDK API to use
android.ndk_api = 21

# (list) Android architectures to build for
android.archs = arm64-v8a, armeabi-v7a

# (bool) Use AndroidX
android.enable_androidx = True

# (list) Add android.gradle_dependencies if needed
# android.gradle_dependencies =

# (list) Java classes to add to the android project
# android.add_src =

# (list) Android AAR archives to add
# android.add_aars =

# (list) Put these files or directories in the apk assets directory.
# android.add_assets =

# (list) Put these files or directories in the apk res directory.
# android.add_resources =

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (bool) Copy libs instead of making a libpymodules.so
android.copy_libs = 1

# (bool) Backup your application data when installing newer versions
android.allow_backup = True

# (str) The format used to package the app for release mode (aab or apk)
android.release_artifact = apk

# (bool) Enable hardware acceleration
android.hardware_accelerated = True

# (list) OUYA Console category. Should be one of GAME or APP
# android.ouya.category = GAME

# (str) Extra manifest XML to write directly inside the <manifest> element
# android.extra_manifest_xml = ./src/android/extra_manifest.xml

# (str) Extra manifest application arguments to write directly inside the <application> tag
# android.extra_manifest_application_arguments =

# (str) Full name including package path of the Java class that implements Android Activity
# android.activity_class_name = org.kivy.android.PythonActivity

# (str) Extra xml to write directly inside the <resources> element of values/strings.xml
# android.extra_strings_xml =

# (bool) Enable AAPT2
android.enable_aapt2 = False

#
# Python for android (p4a) specific
#

# (str) python-for-android fork to use, if not specified, default is used
p4a.fork = kivy

# (str) python-for-android branch to use, defaults to master
p4a.branch = master

# (str) Local version of python-for-android to use
# p4a.source_dir =

# (list) python-for-android bootstraps to use
# p4a.bootstrap = sdl2

# (str) Extra command line arguments to pass to python-for-android
# p4a.extra_args =

#
# Buildozer specific
#

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1

# (bool) If True, use color terminal output
buildozer_color = True

# (str) Path to build artifact storage
build_dir = .buildozer

# (str) Path to build output
bin_dir = ./bin
