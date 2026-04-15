[app]
title = AI ECG Monitor
package.name = aiecgmonitor
package.domain = org.test.ecg
source.dir = . 
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 0.1

# 改动 1：修正了 jnius
requirements = python3,kivy==2.3.0,numpy,pyserial,jnius

orientation = portrait
fullscreen = 0

android.api = 30

android.minapi = 21

android.ndk = 25b
android.build_tools_version = 33.0.0
# 改动 2：增加了 armeabi-v7a，确保所有机型都能解析
android.archs = arm64-v8a, armeabi-v7a

# 改动 3：加入了 Android 12+ 强制需要的新蓝牙权限
android.permissions = BLUETOOTH, BLUETOOTH_ADMIN, BLUETOOTH_SCAN, BLUETOOTH_CONNECT, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

[buildozer] 
log_level = 2
warn_on_root = 0
