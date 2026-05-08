# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\alex2\\youtube_downloader.py'],
    pathex=[],
    binaries=[('C:\\Users\\alex2\\Downloads\\ffmpeg-2026-05-06-git-f2e5eff3ff-essentials_build\\ffmpeg-2026-05-06-git-f2e5eff3ff-essentials_build\\bin\\ffmpeg.exe', '.'), ('C:\\Users\\alex2\\Downloads\\ffmpeg-2026-05-06-git-f2e5eff3ff-essentials_build\\ffmpeg-2026-05-06-git-f2e5eff3ff-essentials_build\\bin\\ffprobe.exe', '.')],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='youtube_downloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='C:\\Users\\alex2\\version_info.txt',
    icon=['C:\\Users\\alex2\\icon.ico'],
)
