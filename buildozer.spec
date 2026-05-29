@@ -1,47 +1,46 @@
[app]
# 应用名称

title = ECGApp


package.name = ecgapp
package.domain = org.ecg

# 源码所在目录（.代表当前目录）
source.dir = .

# 包含的文件扩展名

source.include_exts = py,png,jpg,kv,atlas,ttf

# 你的程序入口文件
# main.py 配置为默认
# 如果你的主程序叫其他名字请修改这里
# source.main = main.py

# 应用版本号
version = 1.0

# 必须的 Python 依赖 (如果需要加其他库放在这里，用逗号隔开)
requirements = python3=3.10,kivy==2.3.0,numpy,pyserial,pyjnius

# 屏幕方向
orientation = portrait

# 开启 Android SDK 自动同意许可，防止 CI 环境卡死
android.accept_sdk_license = True

# 想要最快打包完成，只编译 arm64-v8a 架构（目前99%以上手机支持）
# 要同时兼容新老手机可以用 arm64-v8a,armeabi-v7a；如果想最快打包完只要 arm64-v8a 即可
android.archs = arm64-v8a

# 指定目标 API 版本
android.api = 33
android.minapi = 24

# 是否全屏
fullscreen = 0

[buildozer]
# 日志级别：2代表详细，出错了方便在 GitHub Actions 看日志
log_level = 2

# 遇到警告时不要停
warn_on_root = 1
