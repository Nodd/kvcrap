# -*- mode: python ; coding: utf-8 -*-

from kivy_deps import sdl2, glew

one_file = True
name = "Crapette"
debug = "all"

block_cipher = None
a = Analysis(
    ["main.py"],
    pathex=["./"],
    binaries=[],
    datas=[
        ("crapette/crapette.kv", "crapette/"),
        ("crapette/images/*.png", "crapette/images/"),
        ("crapette/images/png/1x/*.png", "crapette/images/png/1x/"),
        ("crapette/images/png/2x/*.png", "crapette/images/png/2x/"),
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
if one_file:
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
        [],
        name=name,
        debug=debug,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        upx_exclude=[],
        runtime_tmpdir=None,
        console=False,
        # icon="crapette/images/png/2x/suit-spade.png",  # Needs .ico
    )
else:
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name=name,
        debug=debug,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        # icon="crapette/images/png/2x/suit-spade.png",  # Needs .ico
    )
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
        strip=False,
        upx=True,
        upx_exclude=[],
        name=name,
    )
