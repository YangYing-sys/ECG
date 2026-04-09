[app]
title = AI ECG Monitor
package.name = aiecgmonitor
package.domain = org.test.ecg
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 0.1

# 重点：指定了 python3 版本和 kivy 版本，并加上 numpy
requirements = python3,kivy==2.3.0,numpy,pyserial,pyjnius

orientation = portrait
fullscreen = 0

# Android 权限确认
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET, BLUETOOTH, BLUETOOTH_ADMIN, ACCESS_FINE_LOCATION

# 设置 API 级别
android.api = 31
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 0
