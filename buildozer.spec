[app]

# (str) Title of your application
title = Quality Control App

# (str) Package name
package.name = qcapp

# (str) Package domain (needed for android packaging)
package.domain = org.qc.app

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas

# (str) Icon of the application
icon.filename = %(source.dir)s/icon.png

# (str) Presplash image / Splash screen
presplash.filename = %(source.dir)s/bg.png

# (list) Application requirements
requirements = python3,kivy,matplotlib,numpy,pillow

# (str) Application versioning
version = 1.0

# (list) Permissions
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) Target Android API
android.api = 33

# (int) Minimum API supported
android.minapi = 24

# (bool) Accept SDK license
android.accept_sdk_license = True

# (str) Orientation
orientation = portrait

# (bool) Fullscreen
fullscreen = 0

[buildozer]

# (int) Log level
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1
