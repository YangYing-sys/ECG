[app]

title = AI ECG Monitor
package.name = aiecgmonitor
package.domain = org.test

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,csv

version = 0.1

requirements = python3,kivy,numpy,pyjnius,pyserial

orientation = portrait
fullscreen = 0

# 图标
icon.filename = icon.png

# Android API
android.minapi = 24
android.api = 30
android.archs = arm64-v8a

# 权限
android.permissions = BLUETOOTH,BLUETOOTH_ADMIN,ACCESS_FINE_LOCATION,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,INTERNET

# Android 12+ 额外权限（buildozer 老版本有时不支持写在 permissions 里）
android.add_manifest_permission = android.permission.BLUETOOTH_CONNECT
android.add_manifest_permission = android.permission.BLUETOOTH_SCAN

# 保持应用名稳定
android.presplash_color = #FFFFFF

# 避免过度裁剪
android.allow_backup = True

# logcat 方便调试
log_level = 2

[buildozer]
warn_on_root = 0
