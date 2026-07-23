from math import sqrt
import json
import os
from pathlib import Path

from PySide6 import QtWidgets
from PySide6 import QtGui, QtWidgets

class Parametre:    
    # Chemin du fichier caché pour stocker le CodeConnexionAPI
    @staticmethod
    def _getConfigFile():
        config_dir = Path.home() / ".app_config"
        config_dir.mkdir(exist_ok=True)
        return config_dir / "config.json"
    
    CONFIG_FILE = _getConfigFile()
    def __init__(self,w):
        self.window=w
        self.window.setWindowTitle("Liste des paramètres")
        self.chargerCodeConnexionAPI()

    def chargerCodeConnexionAPI(self):
        with open(".clef.txt", "r",encoding="utf-8") as f:
            self.window.CodeConnexionAPI.setText(f.read().strip())

    def sauvegarderCodeConnexionAPI(self):
        with open(".clef.txt", "w",encoding="utf-8") as f:
            f.write(self.window.CodeConnexionAPI.text())
    
    def getCodeConnexionAPI(self):
        """Retourne le CodeConnexionAPI"""
        return self.window.CodeConnexionAPI.text()

    def retour(self):
        self.sauvegarderCodeConnexionAPI()
        print(self.getCodeConnexionAPI())

def getCodeConnexionAPI():
    with open(".clef.txt", "r") as f:
        return f.read().strip()