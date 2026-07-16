# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py','Fiche.py','FormulaireAuteur.py','Caracteristique.py','CaracteristiqueMultiple.py','FormulaireChampsScientifique.py','ListeAFinir.py','Parametre.py','Statistique.py','FormulaireCollection.py'],
    pathex=['.', 'Backend'],
    binaries=[],
    datas=[
        ('UI', 'UI'),
        ('Doc', 'Doc'),
        ('Sortie', 'Sortie'),
        ('Scan', 'Scan'),
        ('Image', 'Image'),
        ('LLMOutput', 'LLMOutput'),
        ('champs_scientifiques.txt', '.'),
    ],
    hiddenimports=['PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets', 'PySide6.QtUiTools', 'openai'],
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
    [],
    exclude_binaries=False,
    name='retro_catalogage',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
