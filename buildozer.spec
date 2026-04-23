[app]

# (str) Title of your application
title = AI心电预警系统

# (str) Package name
package.name = ecgapp

# (str) Package domain (needed for android packaging)
package.domain = org.yangying

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (包含 py, csv 和字体 ttf)
source.include_exts = py,png,jpg,kv,atlas,ttf,csv

# (str) Application versioning
version = 0.1

# (list) Application requirements
# 核心三剑客：numpy (计算), pyserial (串口), pyjnius (调用安卓底层)
requirements = python3,kivy==2.2.1,numpy,pyserial,pyjnius,android

# (list) Supported orientations
orientation = portrait

# (list) Permissions
# 申请所有必要的权限
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, BLUETOOTH, BLUETOOTH_ADMIN, BLUETOOTH_SCAN, BLUETOOTH_CONNECT, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, INTERNET

# (int) Target Android API (MatePad 适配)
android.api = 33

# (int) Minimum API
android.minapi = 21

# (list) The Android architectures to build for (华为 MatePad 是 arm64)
# 只编译 64 位，速度最快，兼容性最好
android.archs = arm64-v8a

# (bool) enables Android auto backup feature
android.allow_backup = True

# (str) python-for-android branch to use
p4a.branch = master

[buildozer]
# (int) Log level (2 代表完整日志，方便报错找原因)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 0
