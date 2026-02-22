# -*- mode: python ; coding: utf-8 -*-
import os

a = Analysis(
    ['src/app.py'],
    pathex=[os.path.abspath('src')],
    datas=[
        ('src/ui/icons/*.png', 'ui/icons'),
        ('src/ui/icons/*.ico', 'ui/icons'),
    ],
    hiddenimports=[
        'core.weighted_matrix',
        'ui.scripts.columns_ui',
        'ui.scripts.matrix_ui',
        'ui.scripts.rows_ui',
    ],
    excludes=[
        'PyQt6.QtBluetooth',
        'PyQt6.QtDBus',
        'PyQt6.QtDesigner',
        'PyQt6.QtHelp',
        'PyQt6.QtMultimedia',
        'PyQt6.QtMultimediaWidgets',
        'PyQt6.QtNetwork',
        'PyQt6.QtNfc',
        'PyQt6.QtOpenGL',
        'PyQt6.QtOpenGLWidgets',
        'PyQt6.QtPositioning',
        'PyQt6.QtPrintSupport',
        'PyQt6.QtQml',
        'PyQt6.QtQuick',
        'PyQt6.QtQuickWidgets',
        'PyQt6.QtSensors',
        'PyQt6.QtSerialPort',
        'PyQt6.QtSql',
        'PyQt6.QtSvg',
        'PyQt6.QtSvgWidgets',
        'PyQt6.QtTest',
        'PyQt6.QtWebChannel',
        'PyQt6.QtWebEngineCore',
        'PyQt6.QtWebEngineWidgets',
        'PyQt6.QtWebSockets',
        'PyQt6.QtXml',
    ],
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name='WeightedDecisionMatrix',
    console=False,
    icon='src/ui/icons/logo.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='WeightedDecisionMatrix',
)
