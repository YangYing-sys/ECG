[app]
title = ECG Monitor
package.name = aiecgmonitor
package.domain = org.test
source.dir = .
# 包含 py代码、图标、字体和CSV权限所需
source.include_exts = py,png,jpg,kv,atlas,ttf,csv

version = 0.1

# 对应 demo4.py 中的所有依赖
requirements = python3,kivy==2.3.0,numpy,pyjnius,pyserial

orientation = portrait
fullscreen = 0

# 安卓专用权限：包含蓝牙、定位、外部存储读写
android.permissions = BLUETOOTH, BLUETOOTH_ADMIN, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, BLUETOOTH_CONNECT, BLUETOOTH_SCAN

# 目标 API 31 是目前最稳定的
android.api = 31
android.minapi = 21
android.sdk = 31
android.ndk = 25b

# 【关键优化】只编译 64 位，防止 GitHub 服务器因编译时间过长而报错
android.archs = arm64-v8a

android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 0
