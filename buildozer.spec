[app]

# (str) Title of your application
title = AI心电预警系统

# (str) Package name
package.name = ecgapp

# (str) Package domain (needed for android packaging)
package.domain = org.yangying

# (str) Source code where the main.py live
source.dir = .

# (str) Application version (加上这一行就修好了！)
version = 0.1

# (list) Source files to include (包含字体文件后缀)
source.include_exts = py,png,jpg,kv,atlas,ttf

# (list) Application requirements
# 注意：务必包含 numpy 和 pyjnius
requirements = python3,kivy,numpy,pyserial,pyjnius,android

# (list) Permissions
android.permissions = BLUETOOTH_SCAN, BLUETOOTH_CONNECT, ACCESS_FINE_LOCATION, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET

# (int) Target Android API
android.api = 33

# (int) Minimum API
android.minapi = 21

# (list) The Android architectures to build for.
# 华为 MatePad 用这个：
android.archs = arm64-v8a
