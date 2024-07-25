# -*- mode: python ; coding: utf-8 -*-
import PyInstaller.config

PyInstaller.config.CONF['distpath'] = './desktop_client'

block_cipher = None

a = Analysis(['../ictrl_be.py'],
             pathex=['.'],
             binaries=[],
             datas=[('../client/build', './client'),
                    ('../log_config.yaml', '.')],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[
                 'algraph',
                 'future',
                 'libfuturize',
                 'pasteurize',
                 'ordlookup',
                 'pefile',
                 'past',
                 'pip',
                 'pkg_resources',
                 'pycparser',
                 'pyinstaller',
                 'wheel',
                 'win32ctypes',
                 'setuptools',
                 # numpy unused
                 # "numpy.array_api", "numpy._typing", "numpy.distutils", "numpy.doc", "numpy.f2py", "numpy.testing",
                 # "numpy.tests", "numpy.typing",
             ],
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
          argv_emulation=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               upx_exclude=[],
               name='ictrl_be')
