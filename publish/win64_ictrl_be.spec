# -*- mode: python ; coding: utf-8 -*-
import PyInstaller.config
PyInstaller.config.CONF['distpath'] = './desktop_client'

block_cipher = None


a = Analysis(['ictrl_be.py'],
             pathex=['C:\\Users\\junha\\PycharmProjects\\ictrl'],
             binaries=[],
             datas=[('./client/build','./client')],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=['setuptools'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts, 
          [],
          exclude_binaries=True,
          name='ictrl_be',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='ictrl_be')
