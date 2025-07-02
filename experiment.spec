# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# PsychoPyの隠れた依存関係を収集
psychopy_hidden = collect_submodules('psychopy')
pyglet_hidden = collect_submodules('pyglet')

# データファイルを収集
datas = []
datas += collect_data_files('psychopy')

# 実験用のファイルを追加
datas += [('task_config.py', '.')]
datas += [('images', 'images')]

# google_config.pyがある場合のみ追加
if os.path.exists('google_config.py'):
    datas += [('google_config.py', '.')]

block_cipher = None

a = Analysis(
    ['experiment.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'psychopy',
        'psychopy.visual',
        'psychopy.core', 
        'psychopy.event',
        'psychopy.data',
        'psychopy.gui',
        'psychopy.logging',
        'psychopy.monitors',
        'pyglet',
        'pyglet.window',
        'pyglet.gl',
        'numpy',
        'pandas',
        'PIL',
        'gspread',
        'google',
        'google.oauth2',
        'google.oauth2.service_account',
        'google.auth',
        'json',
        'datetime',
        'os',
        'sys',
        'random'
    ] + psychopy_hidden + pyglet_hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'test',
        'unittest', 
        'distutils',
        'setuptools',
        'matplotlib.backends._backend_tk'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='expert_novice_experiment',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # ウィンドウのみ表示
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='expert_novice_experiment'
)