[app]

# 基础信息
title = 心电监测系统
package.name = ecgapp
package.domain = org.yangying
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,csv
version = 1.0.0

# Python 依赖（锁定版本避免冲突）
requirements = python3==3.10.0,kivy==2.2.1,numpy==1.24.4,pyserial,pyjnius,android,plyer

# 显示
orientation = portrait
fullscreen = 0

# ========== API / NDK 配置 ==========
android.api = 33
android.minapi = 24
android.ndk = 25b
android.ndk_api = 24          # 🔑 关键参数，解决 numpy 编译问题
android.sdk = 33

# 权限
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, BLUETOOTH, BLUETOOTH_ADMIN, BLUETOOTH_SCAN, BLUETOOTH_CONNECT, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, INTERNET

# 其他
android.archs = arm64-v8a
android.allow_backup = True
android.accept_sdk_license = True
android.numpy = yes

[buildozer]
log_level = 2
warn_on_root = 0
