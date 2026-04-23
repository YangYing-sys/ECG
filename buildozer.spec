[app]
# (str) Title of your application
title = AI心电预警系统

# (str) Package name
package.name = aiecg_matepad

# (str) Package domain (needed for android packaging)
package.domain = org.health.care

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (包含字体文件后缀)
source.include_exts = py,png,jpg,kv,atlas,ttf

# (list) Application requirements
# 注意：一定要包含 pyjnius (调用安卓接口) 和 numpy (算法支持)
requirements = python3,kivy,numpy,pyserial,pyjnius,android

# (str) Custom source folders for requirements
# requirements.source.kivy = ../kivy

# (list) Garden requirements
#garden_requirements =

# (list) Permissions (安卓权限申请)
# 针对蓝牙 HC-05 和 文件保存，必须包含以下权限
android.permissions = BLUETOOTH_SCAN, BLUETOOTH_CONNECT, ACCESS_FINE_LOCATION, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (list) The Android architectures to build for.
# 华为 MatePad Pro 11 建议选 arm64-v8a，为了兼容性可加上 armeabi-v7a
android.archs = arm64-v8a, armeabi-v7a

# (bool) indicates whether the screen should stay on
# 运行心电监测时建议屏幕常亮
android.meta_data = {"android.permission.WAKE_LOCK": "True"}

# (str) Supported orientation (landscape, portrait or all)
# 平板端建议竖屏显示波形效果更好
orientation = portrait

# (bool) Copy library instead of making a libpython.so
android.copy_libs = 1

# (list) List of inclusion filters for assets
# 注意这里增加了 ttf 确保你代码里的字体能被一起打包
source.include_patterns = assets/*,*.ttf

# (str) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (str) Android entry point
python_for_android.entrypoint = main.py

[buildozer]
# (int) log level (0 = error only, 1 = info, 2 = debug)
log_level = 2
