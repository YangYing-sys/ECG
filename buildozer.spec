[app]
# App identity
title = ECG Monitor
package.name = aiecgmonitor
package.domain = org.test
version = 0.1

# Source
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,csv

# Runtime requirements (固定 numpy 以提升 p4a 兼容性)
requirements = python3,kivy==2.3.0,numpy==1.26.4,pyjnius,pyserial

# UI / behavior
orientation = portrait
fullscreen = 0

# 合并后的权限（单行，避免 DuplicateOptionError）
android.permissions = BLUETOOTH, BLUETOOTH_ADMIN, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, BLUETOOTH_CONNECT, BLUETOOTH_SCAN, BLUETOOTH_ADVERTISE

# Android / NDK / SDK 配置
# target SDK (android.api) 决定 manifest targetSdkVersion；android.api >= 31 时需申请细粒度蓝牙权限（已包含上面）
android.api = 33
# 最低支持版本（保留 24，如需更稳定可改为 26）
android.minapi = 24
# 推荐指定稳定 NDK 版本
android.ndk = 25b
# 有些 p4a 版本会使用 ndk_api 字段
android.ndk_api = 24

# 仅构建 64 位以减少 CI 负担
android.archs = arm64-v8a

# 允许备份（可按需关闭）
android.allow_backup = True

# 可选：如果你使用自定义 p4a 分支或本地 recipe，解除注释并修改
# p4a.branch = develop
# p4a.local_recipes = ./recipes

# 可选：如果要自定义图标或 presplash，填入文件路径
# icon.filename = %(source.dir)s/icon.png
# presplash.filename = %(source.dir)s/presplash.png

[buildozer]
log_level = 2
warn_on_root = 0这样呢
