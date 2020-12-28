#!/bin/bash

# change directory into the script's directory
cd "`dirname $0`"

# activate the virtual environment
source venv/bin/activate

# remove the build files and UG_Remote.app which is in the packing dir
rm -rf __pycache__ build dist
rm -rf packing/MacOS/UG_Remote.app

# pack the code using pyinstaller
pyinstaller --clean pyinstaller_specs/macos_UG_Remote.spec

# for some reason the Python excutable needs to be signed
# might be a pyinstaller bug in Python 3.9
codesign -f -s "Junhao Liao" dist/UG_Remote.app/Contents/MacOS/Python

# move the applicaiton into the packing dir
mv dist/UG_Remote.app packing/MacOS/UG_Remote.app

# change directory into the packing dir
cd packing/MacOS

# download the TigerVNC DMG
curl -L -o TigerVNC-1.11.0.dmg "https://bintray.com/tigervnc/stable/download_file?file_path=TigerVNC-1.11.0.dmg"

# detach the previous DMGs
hdiutil detach "/Volumes/UG_Remote\ Installer"
hdiutil detach "/Volumes/TigerVNC-1.11.0"

# create an empty DMG and attach
hdiutil create -ov -size 100m -fs HFS+ -volname "UG_Remote Installer" "before_conversion.dmg"
hdiutil attach "before_conversion.dmg"
hdiutil attach "TigerVNC-1.11.0.dmg"

# create symlinks for the Applications folder
ln -s /Applications "/Volumes/UG_Remote Installer/Applications"
ln -s /Applications "/Volumes/UG_Remote Installer/Applications "
cp mac_bg.png "/Volumes/UG_Remote Installer/.mac_bg.png"
mv UG_Remote.app "/Volumes/UG_Remote Installer/UG_Remote.app"
cp -r De-Quarantine.workflow "/Volumes/UG_Remote Installer/De-Quarantine.workflow"
cp -r "/Volumes/TigerVNC-1.11.0/TigerVNC Viewer 1.11.0.app" "/Volumes/UG_Remote Installer/TigerVNC Viewer 1.11.0.app"
cp "/Volumes/TigerVNC-1.11.0/LICENCE.TXT" "/Volumes/UG_Remote Installer/LICENCE.txt"
cp "/Volumes/TigerVNC-1.11.0/README.rst" "/Volumes/UG_Remote Installer/README.rst"

# open Disk Utility for conversion into write-only DMG 
open /System/Applications/Utilities/Disk\ Utility.app

# open Finder for manual packing
open "/Volumes/UG_Remote Installer"
