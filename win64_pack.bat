rmdir __pycache__ /s/q
rmdir build /s/q
rmdir dist /s/q
rmdir packing\Windows\UG_Remote /s/q
pyinstaller pyinstaller_specs\win64_UG_Remote.spec
move /Y dist\UG_Remote packing\Windows\UG_Remote

cd packing\Windows
"%programfiles(x86)%\NSIS\makensisw.exe" installer.nsi
cd ..\..