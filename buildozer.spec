[app]

# App基本信息
title = AI ECG Monitor
package.name = aiecgmonitor
package.domain = org.test.ecg
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf

# 【修复报错】必须设置版本号
version = 0.1

# 核心依赖 (保持不变)
requirements = python3,kivy==2.3.0,numpy,pyserial,pyjnius

orientation = portrait
fullscreen = 0

# Android 设置
android.accept_sdk_license = True
android.api = 31
android.minapi = 21

# 权限：写存储(存CSV)、蓝牙、定位(蓝牙搜索必选)
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET, BLUETOOTH, BLUETOOTH_ADMIN, ACCESS_FINE_LOCATION

# 架构设置
android.archs = arm64-v8a
android.skip_update = False

[buildozer]
log_level = 2
warn_on_root = 0
