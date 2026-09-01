# -*- mode: python ; coding: utf-8 -*-

block_cipher = None
import certifi
from PyInstaller.utils.hooks import collect_submodules, collect_data_files


openai_hidden = collect_submodules('openai')
openai_datas = collect_data_files('openai')
httpx_hidden = collect_submodules('httpx')
httpcore_hidden = collect_submodules('httpcore')
anyio_hidden = collect_submodules('anyio')
certifi_datas = [(certifi.where(), 'certifi')]

base_datas = [
   ('UI', 'UI'),
   ('Doc', 'Doc'),
   ('Sortie', 'Sortie'),
   ('Scan', 'Scan'),
   ('Image', 'Image'),
   ('LLMOutput', 'LLMOutput'),
   ('champs_scientifiques.txt', '.'),
   ('icon.ico', '.'),
]

hidden_imports = [
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'PySide6.QtUiTools',
    'certifi',
    'ssl',
    '_ssl',
    'httpx',
    'httpcore',
    'anyio',
    'h11',
    'sniffio',
    'pydantic',
    'pydantic_core',
    'jiter',
] + openai_hidden + httpx_hidden + httpcore_hidden + anyio_hidden

a = Analysis(['main.py','app_paths.py','Caracteristique.py','CaracteristiqueMultiple.py','Fiche.py','FormulaireAuteur.py','FormulaireChampsScientifique.py','FormulaireCollection.py','ListeAFinir.py','Parametre.py','Statistique.py'],
          pathex=['.','Backend'],
          binaries=[],
          datas=base_datas + openai_datas + certifi_datas,
         hiddenimports=hidden_imports,
            hookspath=[],
            hooksconfig={},
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
          [],
          exclude_binaries=True,
          name='Biblinum',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True,
            disable_windowed_traceback=False,
            argv_emulation=False,
            target_arch=None,
            codesign_identity=None,
            entitlements_file=None,
            icon='icon.ico',)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='Biblinum')