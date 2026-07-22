[app]

# (str) Title of your application
title = Quality Control App

# (str) Package name
package.name = qcapp

# (str) Package domain (needed for android packaging)
package.domain = org.qc.app

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (process one file or space separated)
source.include_exts = py,png,jpg,kv,atlas

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy,matplotlib,numpy,pillow

# (str) Application versioning (method 1)
version = 1.0

# (list) Permissions
android.permissions = WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) Target Android API, should be high enough, e.g. 33 or 34
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (bool) If True, then skip trying to update the Android sdk
android.accept_sdk_license = True

# (str) Orientation (landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = false, 1 = true)
warn_on_root = 1
