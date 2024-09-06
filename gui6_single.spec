import sys

block_cipher = None

a = Analysis(['gui6.py'],
             pathex=['.'],
             binaries=[],
             datas=[('loading_spinner.gif', '.'),
                    ('dark_style.qss', '.'),
                    ('light_style.qss', '.')],
             hiddenimports=['PyQt6.sip'],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          name='Object Detection Dataset Converter',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          runtime_tmpdir=None,
          upx=True,
          console=False)

# Adjust the executable extension based on the platform
if sys.platform.startswith('win'):
    exe.name += '.exe'
elif sys.platform.startswith('darwin'):
    app = BUNDLE(coll,
                 name='CV Converter.app',
                 icon=None,
                 bundle_identifier=None)