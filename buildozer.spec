[app]
title = ECG Monitor
package.name = aiecgmonitor
package.domain = org.test
version = 0.1

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,csv

#Runtime requirements（移除 numpy 的精确版本以避免 CI 在某些 recipe 上尝试 checkout 不存在的 ref）
requirements = python3,kivy==2.3.0,pyjnius,pyserial,numpy

orientation = portrait
fullscreen = 0

#合并后的权限（单行）
android.permissions = BLUETOOTH, BLUETOOTH_ADMIN, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, BLUETOOTH_CONNECT, BLUETOOTH_SCAN, BLUETOOTH_ADVERTISE

Android / NDK / SDK 配置
android.api = 33
android.minapi = 24
android.ndk = 25b
android.ndk_api = 24

#仅构建 64 位
android.archs = arm64-v8a

android.allow_backup = True

#可选：自定义 p4a 分支或本地 recipe
p4a.branch = develop
p4a.local_recipes = ./recipes
#[buildozer]
log_level = 2
warn_on_root = 0
