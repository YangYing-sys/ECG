[app]
title = AI ECG Monitor
package.name = aiecgmonitor
package.domain = org.test.ecg
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 0.1

# 【注意】暂时去掉了 numpy，先确保能出一版 APK
requirements = python3,kivy==2.3.0,pyserial,pyjnius

orientation = portrait
fullscreen = 0

android.api = 31
android.minapi = 21
# 锁定一个稳定的 SDK/NDK 组合
android.ndk = 25b
android.build_tools_version = 33.0.0
android.archs = arm64-v8a

android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET, BLUETOOTH, BLUETOOTH_ADMIN, ACCESS_FINE_LOCATION

[buildozer]
log_level = 2
warn_on_root = 0
