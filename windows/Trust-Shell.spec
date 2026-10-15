# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

hiddenimports=['requests', 'json', 'sqlite3', 'cryptography'],


a = Analysis(
    ['../main.py'],  # Points back to the root entry point if main.py is in the repo root
    pathex=['../'],
    binaries=[],
    datas=[],        # Left empty since there is no assets folder
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Trust-Shell',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,           # Change to True if you need a command prompt visible for logs
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
