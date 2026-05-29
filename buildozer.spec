[app]
# (str) Title of your application
title = ECG App

# (str) Package name
package.name = ecgapp

# (str) Package domain (needed for android packaging)
package.domain = org.test

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf

# (str) Application versioning (method 1)
version = 0.1

# (list) Application requirements
# ✅ 包含你代码中所有的库：kivy, numpy, pyserial
# ✅ pyjnius 是安卓调用系统功能必须的
requirements = python3,kivy==2.3.0,numpy,pyserial,pyjnius

# (str) Supported orientations (landscape, sensorLandscape, portrait or all)
orientation = landscape

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (list) Permissions
# ✅ 申请了蓝牙和文件读写权限（用于串口通讯和保存CSV）
android.permissions = BLUETOOTH, BLUETOOTH_ADMIN, BLUETOOTH_CONNECT, BLUETOOTH_SCAN, INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 33

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (list) The Android archs to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
# ✅ 华为平板推荐包含 arm64-v8a
android.archs = arm64-v8a, armeabi-v7a

# (bool) enables Android auto backup feature (OS >= 6.0)
android.allow_backup = True

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = off, 1 = on)
warn_on_root = 1
