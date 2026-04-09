[app]
title = AI ECG Monitor
package.name = aiecgmonitor
package.domain = org.test.ecg
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 0.1

# 依赖保持不变
requirements = python3,kivy==2.3.0,numpy,pyserial,pyjnius

orientation = portrait
fullscreen = 0

# Android 核心配置：锁定版本防止乱升级
android.api = 31
android.minapi = 21
android.ndk = 25b
# 【关键修复】锁定 build-tools 版本
android.build_tools_version = 33.0.0
android.archs = arm64-v8a

android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET, BLUETOOTH, BLUETOOTH_ADMIN, ACCESS_FINE_LOCATION

[buildozer]
log_level = 2
warn_on_root = 0
