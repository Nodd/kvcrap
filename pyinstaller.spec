# -*- mode: python ; coding: utf-8 -*-

# On conda, it needs : pip install kivy-deps.sdl2 kivy-deps.glew
from kivy_deps import sdl2, glew
from kivy.tools.packaging.pyinstaller_hooks import (
    get_deps_minimal,
    hookspath,
    runtime_hooks,
)

one_file = True
name = "Crapette"
debug = "all"

config = get_deps_minimal(
    audio=None,
    camera=None,
    clipboard=None,
    image=["img_sdl2"],
    spelling=None,
    text=["text_sdl2"],
    video=None,
    window=["window_sdl2"],
)
hiddenimports = []  # config["hiddenimports"] + ["kivy.weakmethod"]
excludes = []  # config["excludes"]
binaries = []  # config["binaries"]
block_cipher = None

a = Analysis(
    ["src/main.py"],
    pathex=["./src"],
    datas=[
        ("crapette/crapette.kv", "crapette/"),
        ("crapette/images/*.png", "crapette/images/"),
        ("crapette/images/png/2x/*.png", "crapette/images/png/2x/"),
    ],
    hookspath=[],  # hookspath(),
    runtime_hooks=[],  # runtime_hooks(),
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    hiddenimports=hiddenimports,
    excludes=excludes,
    binaries=binaries,
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
