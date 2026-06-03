[app]
title = ECG Monitor
package.name = aiecgmonitor
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,csv
version = 0.1

# 维持 2.3.0 版本的 Kivy 最稳定
requirements = python3,kivy==2.3.0,numpy,pyjnius,pyserial

orientation = portrait
fullscreen = 0

android.permissions = BLUETOOTH, BLUETOOTH_ADMIN, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, BLUETOOTH_CONNECT, BLUETOOTH_SCAN

# 【核心修复：针对 numpy 报错】
android.api = 33
android.minapi = 24
android.ndk = 25b

# 只编译 64 位，防止 GitHub 内存爆炸
android.archs = arm64-v8a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 0
