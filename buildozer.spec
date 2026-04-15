[app]
title = AI ECG Monitor
package.name = aiecgmonitor
package.domain = org.test

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,csv

version = 0.1

# Kivy和手机外设交互的核心库依赖
requirements = python3,kivy,numpy,pyjnius,pyserial

orientation = portrait
fullscreen = 0
icon.filename = icon.png

# 【关键配置】兼容性与不崩溃的保证！
android.api = 30
android.minapi = 21
android.archs = arm64-v8a

# 核心系统权限申请配置
android.permissions = BLUETOOTH,BLUETOOTH_ADMIN,ACCESS_FINE_LOCATION,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,INTERNET
android.add_manifest_permission = android.permission.BLUETOOTH_CONNECT
android.add_manifest_permission = android.permission.BLUETOOTH_SCAN

log_level = 2
