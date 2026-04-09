[app]

# (str) 你的 App 名字
title = AI ECG Monitor

# (str) 包名（小写，建议用这个名，不容易冲突）
package.name = aiecgmonitor

# (str) 组织名
package.domain = org.ecg

# (str) 源代码所在目录
source.dir = .

# (list) 包含的文件后缀 (必须包含 ttf，因为你代码里用了中文字体和表情包字体)
source.include_exts = py,png,jpg,kv,atlas,ttf

# (list) 你的代码里 import 的所有库（最关键的一行）
# 包括了：python3, kivy, numpy, pyserial(名写为serial), pyjnius(用于安卓底层调用)
requirements = python3,kivy==2.3.0,numpy,pyserial,pyjnius

# (str) 屏幕方向
orientation = portrait

# ----------------------------------
# Android 配置
# ----------------------------------

# (bool) 是否接受 SDK 协议 (GitHub 打包必填 True)
android.accept_sdk_license = True

# (int) 目标安卓 API 级别
android.api = 33

# (int) 最低支持安卓版本
android.minapi = 21

# (list) 你的项目申请的权限（根据你的代码：存CSV数据 + 串口通信/蓝牙）
# 包含了：读写存储、互联网、蓝牙、精确定位（安卓蓝牙搜寻必须）
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET, BLUETOOTH, BLUETOOTH_ADMIN, ACCESS_FINE_LOCATION

# (list) 包含的服务（如果有） - 无

# (str) 安卓架构 (建议选 arm64-v8a 最适配现代手机，构建也快)
android.archs = arm64-v8a

# (bool) 允许跳过更新
android.skip_update = False

# (str) 这里的设置可以防止某些串口库报错
android.meta_data = com.google.android.gms.version=@integer/google_play_services_version

# ----------------------------------
# Buildozer 运行配置
# ----------------------------------

[buildozer]

# 日志级别
log_level = 2

# 警告级别
warn_on_root = 0