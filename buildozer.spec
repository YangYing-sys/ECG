[app]
title = ECG Monitor
package.name = aiecgmonitor
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,csv
version = 0.1

# 关键：固定 numpy 版本为 1.26.4（与 python-for-android 兼容性最好）
requirements = python3,kivy==2.3.0,numpy==1.26.4,pyjnius,pyserial

orientation = portrait
fullscreen = 0

# 安卓权限（按需调整）
android.permissions = BLUETOOTH, BLUETOOTH_ADMIN, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, BLUETOOTH_CONNECT, BLUETOOTH_SCAN

# 平台/NDK 设置（确保 minapi >= 24，以满足 numpy 的最低要求）
android.api = 33
android.minapi = 24
android.ndk = 25b
# 可额外指定 ndk api（部分 p4a 版本使用此字段）
android.ndk_api = 24

# 性能与稳定性：仅构建 64 位以降低 CI 负担
android.archs = arm64-v8a

android.allow_backup = True

# 其他（可按需调）
android.permissions = BLUETOOTH, BLUETOOTH_ADMIN, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE
# 可选：如果你需要自定义 p4a 分支或自定义 recipe，解注释下面两行并添加自定义 recipes
# p4a.branch = develop
# p4a.local_recipes = ./recipes

[buildozer]
log_level = 2
warn_on_root = 0
