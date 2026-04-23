[app]

# (str) Title of your application
title = AI心电预警系统

# (str) Package name
package.name = ecgapp

# (str) Package domain (needed for android packaging)
package.domain = org.yangying

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
# 这里加入了 ttf 和 csv，确保你的中文字体文件能被打包进去！！
source.include_exts = py,png,jpg,kv,atlas,ttf,csv

# (str) Application versioning (这个就是修复你刚才报错的关键)
version = 0.1

# (list) Application requirements
# 包含了 numpy进行计算，pyserial进行串口/蓝牙通信，pyjnius进行安卓原生API调用
requirements = python3,kivy,numpy,pyserial,pyjnius,android

# (str) Presplash of the application
# presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
# icon.filename = %(source.dir)s/data/icon.png

# (list) Supported orientations
# Valid options are: landscape, portrait, portrait-reverse or landscape-reverse
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (string) Presplash background color (for android toolchain)
android.presplash_color = #FFFFFF

# (list) Permissions
# 包含了存储权限(保存CSV)和蓝牙/位置权限(用于可能的硬件连接)
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, BLUETOOTH, BLUETOOTH_ADMIN, BLUETOOTH_SCAN, BLUETOOTH_CONNECT, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (str) Android NDK version (if empty, it will be automatically downloaded.)
# android.ndk = 25b

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess Internet downloads or save time
# when an update is due and you just want to test/build your package
android.skip_update = False

# (bool) If True, then automatically accept SDK license
# 非常重要：这能让 Github Actions 遇到协议框时自动同意，防止卡死
android.accept_sdk_license = True

# (list) The Android architectures to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
# In past values like armeabi, mips and mips64 were supported.
# 专为你的华为 MatePad 优化的64位架构，不但运行快，打包也省时间！
android.archs = arm64-v8a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (str) python-for-android branch to use, defaults to master
p4a.branch = master

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 0
