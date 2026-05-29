[app]

# (str) Application title
title = 智能心电监测系统

# (str) Package name (no spaces, lowercase)
package.name = ecgapp

# (str) Package domain
package.domain = org.yangying

# (str) Source code directory
source.dir = .

# (list) File extensions to include
source.include_exts = py,png,jpg,kv,atlas,ttf,csv

# (str) Application version
version = 1.0.0

# (list) Python requirements
requirements = python3,kivy==2.2.1,numpy,pyserial,pyjnius,android,plyer

# (str) Presplash image (optional)
# presplash.filename = %(source.dir)s/presplash.png

# (str) Icon image (optional)
# icon.filename = %(source.dir)s/icon.png

# (list) Supported orientations
orientation = portrait

# (bool) Fullscreen mode
fullscreen = 0

# (list) Android permissions
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, BLUETOOTH, BLUETOOTH_ADMIN, BLUETOOTH_SCAN, BLUETOOTH_CONNECT, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, INTERNET

# (int) Target Android API level
android.api = 33

# (int) Minimum Android API level
android.minapi = 21

# (int) Target SDK version
android.target_sdk = 33

# (list) Android architectures to build
android.archs = arm64-v8a

# (bool) Enable Android backup
android.allow_backup = True

# (str) Python-for-Android branch
p4a.branch = master

# (str) Android NDK version
android.ndk = 23b

# (str) Android SDK version
android.sdk = 30

# (bool) Auto accept SDK license
android.accept_sdk_license = True

# (bool) Freshen requirements
android.freshen_requirements = True

# (list) Gradle dependencies (optional)
# android.gradle_dependencies = 'com.android.support:support-v4:28.0.0'

[buildozer]

# (int) Log level (0=error,1=warn,2=info,3=debug)
log_level = 2

# (bool) Warn if running as root
warn_on_root = 0
