[app]
title = ECG App
package.name = ecgapp
package.domain = org.yangying
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,csv
source.include_patterns = assets/*,images/*,fonts/*
source.exclude_exts = spec
source.exclude_dirs = tests, bin, venv, .git, __pycache__
source.exclude_patterns = *.pyc,*.pyo,*.git/*
version = 1.0

# Critical: Needed to fix the build errors
requirements = python3,kivy,numpy,pyjnius,pyserial

orientation = portrait
fullscreen = 0

[buildozer]
log_level = 2
warn_on_root = 1
buildozer_color = 1 

[app:android]
android.fullscreen = 0
android.entrypoint = org.kivy.android.PythonActivity

# Critical: Needed for HC-05 Classic Bluetooth to work in Android 12+
android.permissions = BLUETOOTH,BLUETOOTH_ADMIN,BLUETOOTH_CONNECT,BLUETOOTH_SCAN,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# Stable parameters for compilation (Removed the deprecated android.sdk variable)
android.api = 31
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a, armeabi-v7a
android.enable_androidx = True

android.logcat_filters = *:S python:D
android.copy_libs = 1
android.allow_backup = True
android.release_artifact = apk
android.hardware_accelerated = True
android.enable_aapt2 = False

[app:p4a]
p4a.fork = kivy
p4a.branch = master
