[app]

title = 智能心电监测系统
package.name = ecgapp
package.domain = org.yangying
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,csv
version = 1.0.0

# Python 3.10 + Kivy 2.2.1
requirements = python3==3.10.0,kivy==2.2.1,numpy==1.24.4,pyserial,pyjnius,android,plyer

orientation = portrait
fullscreen = 0

# 权限
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, BLUETOOTH, BLUETOOTH_ADMIN, BLUETOOTH_SCAN, BLUETOOTH_CONNECT, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, INTERNET

# ========== 关键配置 ==========
# 目标 API（应用运行的 Android 版本）
android.api = 33

# 最低支持 API（numpy 要求 >= 24）
android.minapi = 24

# NDK 编译 API（numpy 编译必须为 24）
android.ndk_api = 24

# NDK 版本
android.ndk = 25b

# SDK 版本
android.sdk = 30

# 其他
android.accept_sdk_license = True
android.numpy = yes
android.archs = arm64-v8a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 0
