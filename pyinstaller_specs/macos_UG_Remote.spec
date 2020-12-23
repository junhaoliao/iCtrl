# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['UG_Remote.py'],
             pathex=['/Users/junhao/PycharmProjects/UG_Remote'],
             binaries=[],
             datas=[
                ('Gnome-view-refresh-20x20.png','.'),
                ('TigerVNC.app','./TigerVNC.app'),
                ('TigerVNC_LICENCE.txt','.')
             ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
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
          name='UG_Remote',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='UG_Remote')
app = BUNDLE(coll,
             name='UG_Remote.app',
             icon='icon.icns',
             bundle_identifier='ca.junhao.ugremote',
             version='5.0.0')
