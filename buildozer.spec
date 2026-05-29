[app]
# 应用名称和包名
title = ECG Assist System
package.name = ecg_app
package.domain = com.ai.ecg

# 源代码目录和文件过滤清单
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf

# 核心依赖项设置 (包含 numpy, pyserial 串口, pyjnius 底层调用)
requirements = python3,kivy,numpy,pyserial,pyjnius

# 屏幕方向 (可以设置为 landscape, portrait 或 all)
orientation = portrait

# 对应高版本 Android/HarmonyOS 的系统权限申请
# 包含读写闪存和蓝牙连接、蓝牙搜索权限
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, BLUETOOTH, BLUETOOTH_ADMIN, BLUETOOTH_CONNECT, BLUETOOTH_SCAN, INTERNET

# 目标 Android API 版本 (HarmonyOS 4/基于 Android 12-13，建议设置 33)
android.api = 33
android.minapi = 21
android.ndk_api = 21

# 打包架构类型：华为 MatePad Pro 11 采用骁龙系列 64 位芯片，必须支持 arm64-v8a
android.archs = arm64-v8a

# 自适应启动图与图标配置 (可维持默认)
icon.filename = %(source.dir)s/icon.png
# 如果没有icon.png，可以先注释该行，buildozer 会使用默认图标

[buildozer]
log_level = 2
warn_on_root = 1
