[app]
title = 心电预警系统
package.name = ecgmonitor
package.domain = org.ecg
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,ttc

# 主程序入口已修改为 main.py
main = main.py

version = 1.0

# 你的代码需要的 Python 库依赖
requirements = python3,kivy==2.3.0,pyjnius,android,pyserial,numpy=1.26.4

# 针对 Android 10+ 系统的配置
android.archs = arm64-v8a
android.minapi = 24
android.api = 33
android.ndk = 25b

# 蓝牙和存储权限
android.permissions = BLUETOOTH, BLUETOOTH_ADMIN, BLUETOOTH_CONNECT, BLUETOOTH_SCAN, ACCESS_FINE_LOCATION, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

orientation = portrait
fullscreen = 0
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
