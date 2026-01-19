# -*- mode: python ; coding: utf-8 -*-
# Alternative spec file using --onedir instead of --onefile
# This creates a folder with the executable and all dependencies
# Sometimes works better with PyQt6 DLLs
from PyInstaller.utils.hooks import collect_all

datas = [('icon.png', '.')]
binaries = []
hiddenimports = ['pkgutil']

# Collect PyQt6 - this includes DLLs, data files, and modules
tmp_ret = collect_all('PyQt6')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

# Exclude unnecessary PyQt6 modules to reduce complexity
excludes = [
    'PyQt6.Qt3DAnimation', 'PyQt6.Qt3DCore', 'PyQt6.Qt3DExtras', 'PyQt6.Qt3DInput',
    'PyQt6.Qt3DLogic', 'PyQt6.Qt3DRender', 'PyQt6.QtBluetooth', 'PyQt6.QtCharts',
    'PyQt6.QtDataVisualization', 'PyQt6.QtLocation', 'PyQt6.QtMultimedia',
    'PyQt6.QtMultimediaWidgets', 'PyQt6.QtNfc', 'PyQt6.QtOpenGL', 'PyQt6.QtOpenGLWidgets',
    'PyQt6.QtPositioning', 'PyQt6.QtQml', 'PyQt6.QtQuick', 'PyQt6.QtQuick3D',
    'PyQt6.QtQuickWidgets', 'PyQt6.QtRemoteObjects', 'PyQt6.QtSensors',
    'PyQt6.QtSerialPort', 'PyQt6.QtSql', 'PyQt6.QtSvg', 'PyQt6.QtSvgWidgets',
    'PyQt6.QtTest', 'PyQt6.QtWebChannel', 'PyQt6.QtWebEngine', 'PyQt6.QtWebEngineCore',
    'PyQt6.QtWebEngineWidgets', 'PyQt6.QtWebSockets', 'PyQt6.QtXml', 'PyQt6.QtXmlPatterns',
    'PyQt6.QtScxml', 'PyQt6.QtStateMachine', 'PyQt6.QtWebView'
]

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon='icon.ico',
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='app',
)
