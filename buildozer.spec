[app]
# (string) 应用的显示名称
title = AI ECG System

# (string) 包名
package.name = aiecgapp

# (string) 域（用于生成包名，例如 com.ai.aiecgapp）
package.domain = com.ai

# (string) 源代码所在目录（. 代表当前目录）
source.dir = .

# (list) 包含的文件后缀，必须包含 ttf 字体才能正常显示中文和表情
source.include_exts = py,png,jpg,kv,atlas,ttf

# ====== 修复关键点：添加版本号 ======
version = 0.1

# (list) 你的代码中所引用的依赖库
# 注意：numpy 编译较慢，第一次打包需要耐心等待
requirements = python3,kivy,numpy,pyserial,pyjnius

# (string) 屏幕方向
orientation = portrait

# (list) 华为 MatePad 平板调试蓝牙和存储所需的权限
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, BLUETOOTH, BLUETOOTH_ADMIN, BLUETOOTH_CONNECT, BLUETOOTH_SCAN, INTERNET

# (int) 目标 Android API，这里设为 33 (兼容 HarmonyOS 4)
android.api = 33
android.minapi = 21
android.ndk_api = 21

# (list) 华为 MatePad 等现代设备的 CPU 架构
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
