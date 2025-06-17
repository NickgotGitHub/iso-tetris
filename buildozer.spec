[app]
# (str) Title of your application
title = Tetris

# (str) Package name
package.name = Tetris

# (str) Package domain (needed for iOS packaging)
package.domain = org.test

# (str) Source code directory where main.py lives
source.dir = .

# (list) Source files to include (leave empty to include all files)
source.include_exts = py,kv,png,jpg,mp3,ttf,otf,db

# (list) List of inclusions using pattern matching
source.include_patterns = 
    Assets/*,
    Assets/Audios/*,
    Assets/Fonts/*,
    Assets/Sprites/*,
    screens/*,
    *.db

# (list) List of directories to exclude
source.exclude_dirs = tests, bin, venv

# (str) Application version
version = 0.1

# (list) Application requirements (specify Python version and needed packages)
requirements = python3==3.11.7,kivy,plyer

# (list) Supported orientations
orientation = portrait

#
# OSX / iOS Specific Settings
#

# (int) Major version of Python used by the app (for iOS packaging)
osx.python_version = 3

# (str) Kivy version to use for iOS packaging (update as needed)
osx.kivy_version = 2.2.0

#
# iOS Specific Settings
#

# (str) URL for the kivy-ios toolchain repository
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
# (str) Branch to use from the kivy-ios repository
ios.kivy_ios_branch = master

# (str) URL for ios-deploy (used to deploy apps to devices)
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
# (str) Branch to use for ios-deploy
ios.ios_deploy_branch = 1.10.0

# (bool) Allow code signing; set to false during development
ios.codesign.allowed = false

ios.codesign.debug = Apple Development: nicholas.salmon@glenmuirhighschool.edu.jm (ZWDDBU3U2B)
ios.codesign.development_team.debug = ZWDDBU3U2B


# (Optional) iOS manifest URLs (if you wish to supply app and icon links)
# ios.manifest.app_url =
# ios.manifest.display_image_url =
# ios.manifest.full_size_image_url =

[buildozer]
# (int) Log level: 0 = error only, 1 = info, 2 = debug (with command output)
log_level = 2

# (int) Display warning if Buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (Optional) Path to build artifact storage (if desired)
# build_dir = ./.buildozer

# (Optional) Path to build output storage (e.g. for .ipa files)
# bin_dir = ./bin