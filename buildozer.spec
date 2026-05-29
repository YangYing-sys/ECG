[app]
# (str) Title of your application
title = ECG App

# (str) Package name
package.name = ecgapp

# (str) Package domain (needed for android packaging)
package.domain = org.test

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (leave empty to include all files)
source.include_exts = py,png,jpg,kv,atlas,ttf

# (str) Application versioning
version = 0.1

# (list) Application requirements
requirements = python3,kivy==2.3.0,numpy,pyserial,pyjnius

# (str) Supported orientations
orientation = landscape

# (bool) Fullscreen
fullscreen = 1

# (list) Permissions
android.permissions = BLUETOOTH, BLUETOOTH_ADMIN, BLUETOOTH_CONNECT, BLUETOOTH_SCAN, INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) Target Android API
android.api = 33
android.minapi = 21
android.sdk = 33

# (str) Android NDK version
android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (list) Android architectures
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature (OS >= 6.0)
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
