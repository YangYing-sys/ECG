[app]

# (str) Title of your application
title = 智能心电监测系统

# (str) Package name
package.name = ecgapp

# (str) Package domain (needed for android packaging)
package.domain = org.yangying

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas,ttf,csv

# (str) Application versioning
version = 1.0.0

# (list) Application requirements
# kivy 版本建议锁定稳定版，添加 plyer 用于文件访问
requirements = python3,kivy==2.2.1,numpy,pyserial,pyjnius,android,plyer

# (list) Supported orientations
orientation = portrait

# (list) Permissions
# Android 12+ 蓝牙权限需要分开声明
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, BLUETOOTH, BLUETOOTH_ADMIN, BLUETOOTH_SCAN, BLUETOOTH_CONNECT, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, INTERNET

# (int) Target Android API
android.api = 33

# (int) Minimum API (Android 5.0+，兼容更多设备)
android.minapi = 21

# (int) Target SDK version
android.target_sdk = 33

# (list) Android architectures
android.archs = arm64-v8a

# (bool) enables Android auto backup feature
android.allow_backup = True

# (str) python-for-android branch to use
p4a.branch = master

# (str) Android NDK version
android.ndk = 23b

# (str) Android SDK version
android.sdk = 30

# (list) Gradle dependencies for Bluetooth (可选，提高蓝牙稳定性)
android.gradle_dependencies = 'com.android.support:support-v4:28.0.0'

# (bool) If True, try to download prebuilt packages for Android (加速打包)
android.freshen_requirements = True

[buildozer]

# (int) Log level (2 输出详细日志)
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 0
