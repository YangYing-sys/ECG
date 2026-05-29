[app]
title = ECGApp
package.name = ecgapp
package.domain = org.ecg
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 1.0
# 在此不要写 python3=3.11，Python 版本在 workflow 中固定
requirements = python3,kivy==2.3.0,numpy,pyserial,pyjnius
orientation = portrait
# Manifest 权限（包含 Android 12+ 的蓝牙权限）
android.permissions = BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_CONNECT,BLUETOOTH_SCAN,BLUETOOTH_ADVERTISE,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION
android.accept_sdk_license = True
# 若要兼容更多设备可设为 "arm64-v8a,armeabi-v7a"
android.archs = arm64-v8a,armeabi-v7a
android.api = 33
android.minapi = 24
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1
