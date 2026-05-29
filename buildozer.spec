[app]

# 应用标题
title = 心电预警系统
package.name = ecgmonitor
package.domain = org.ecg

# 源文件
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf

# 主程序入口
main = demo4.py

# 版本
version = 1.0

# 需求
requirements = python3,kivy==2.3.0,pyjnius,android,pyserial,numpy,plyer

# Android 配置
android.arch = arm64-v8a
android.minapi = 24  # Android 7.0
android.api = 33  # Android 13
android.ndk = 25b
android.sdk = 33
android.gradle_dependencies = 'com.android.support:appcompat-v7:28.0.0'
android.p4a_dir = p4a

# 权限
android.permissions = INTERNET,BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_CONNECT,BLUETOOTH_SCAN,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# 特性
android.features = android.hardware.bluetooth

# 图标（可选）
# icon.filename = %(source.dir)s/assets/icon.png

# 方向
orientation = portrait

# 其他配置
fullscreen = 0
log_level = 2
android.accept_sdk_license = True

# Kivy 配置
osx.python_version = 3
osx.kivy_version = 2.3.0

[buildozer]
log_level = 2
warn_on_root = 1
