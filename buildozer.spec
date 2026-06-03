[app]

# (str) Title of your application
title = 心电预警系统

# (str) Package name
package.name = aiecgnonitor

# (str) Package domain (needed for android packaging)
package.domain = org.ecg.monitor

# (str) Source code directory
source.dir = .

# (list) Source files to include (file extensions)
# 必须包含 ttf 格式以引入你的字体文件
source.include_exts = py,png,jpg,kv,atlas,ttf

# (str) Application version
version = 1.0

# (list) Application requirements
# 包含 kivy、numpy（波形缓冲处理）以及 pyserial/pyjnius 依赖
requirements = python3,kivy,numpy,pyserial,pyjnius,android

# (str) Supported orientations
# 你的布局为垂直布局，建议锁定为 portrait（竖屏）
orientation = portrait

# (bool) Use fullscreenmode or not
fullscreen = 0

# ==============================================================================
# Android specific configuration
# ==============================================================================

# (list) Permissions
# 包含了你的代码需要的存储读写权限，以及蓝牙连接和定位权限（蓝牙扫描必须）
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, BLUETOOTH, BLUETOOTH_ADMIN, BLUETOOTH_CONNECT, BLUETOOTH_SCAN, ACCESS_FINE_LOCATION, MOUNT_UNMOUNT_FILESYSTEMS

# (int) Target device API
android.api = 33

# (int) Minimum API required
android.minapi = 21

# (list) The Android archs to build for (64位华为平板必须要 arm64-v8a)
android.archs = armeabi-v7a, arm64-v8a

# (bool) Enable AndroidX support (required for modern android libraries)
android.enable_androidx = True

# (bool) Copy library instead of making a symlink
# android.copy_libs = 1

# (list) Java classes to bootstrap (Leave commented unless needed)
# android.entrypoint = org.kivy.android.PythonActivity

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with compiler output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
