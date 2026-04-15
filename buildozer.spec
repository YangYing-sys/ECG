[app]

# 应用的名称 (安装在手机上显示的完整名称)
title = AI ECG Monitor

# 包名 (非常重要！全小写英文，不要有空格，用来区分旧版本)
package.name = aiecgmonitor

# 域名前缀
package.domain = org.test

# 源代码所在目录 ('.' 代表当前目录)
source.dir = .

# 【关键】允许打包进 APK 的文件类型！ (必须加 ttf 和 csv，否则字体加载失败直接闪退)
source.include_exts = py,png,jpg,kv,atlas,ttf,csv

# 应用版本号
version = 0.1

# 【关键】Python 依赖包！打包时会自动下载这些
requirements = python3,kivy,numpy,pyjnius,pyserial

# 屏幕方向 (设置竖屏)
orientation = portrait

# 是否全屏 (0=显示顶部状态栏，时间/电量等)
fullscreen = 0

# 如果你有图标，取消下一行的注释，并保证目录下有个 icon.png
# icon.filename = icon.png

# ==========================================
# 安卓 (Android) 专属配置
# ==========================================

# 【极度关键】申请安卓所需的系统权限
# 涵盖：蓝牙、蓝牙管理、精准定位、粗略定位、读写存储、网络
# 涵盖了 Android 12 以上强制新增的 BLUETOOTH_CONNECT 和 BLUETOOTH_SCAN
android.permissions = BLUETOOTH, BLUETOOTH_ADMIN, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, INTERNET, BLUETOOTH_CONNECT, BLUETOOTH_SCAN

# 目标 Android API 版本 (建议31，能完美兼容目前市面上的新老手机)
android.api = 31

# 最低支持的 Android API 版本 (21 代表支持安卓 5.0 以上)
android.minapi = 21

# 打包的 CPU 架构 (同时支持绝大部分新旧手机和模拟器)
android.archs = arm64-v8a, armeabi-v7a

# 允许应用备份
android.allow_backup = True

# ==========================================
# Buildozer 打包环境配置
# ==========================================
[buildozer]

# 日志级别 (2=输出详细打包日志，万一报错可以看清原因)
log_level = 2

# 忽略 root 警告 (在 GitHub Actions 自动化打包里必须设为 0)
warn_on_root = 0
