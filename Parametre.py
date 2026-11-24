from math import sqrt
import json
import os
import sys
from pathlib import Path

from PySide6 import QtWidgets
from PySide6 import QtGui, QtWidgets

from app_paths import get_exe_dir


def _get_clef_path() -> Path:
    """Chemin persistant de la clé API (à côté de l'exe en build PyInstaller)."""
    return Path(get_exe_dir()) / ".clef.txt"


def _read_api_key() -> str:
    clef_path = _get_clef_path()
    if not clef_path.is_file():
        return ""
    return clef_path.read_text(encoding="utf-8").strip()


def has_api_key() -> bool:
    return bool(_read_api_key())


def validate_api_key(key: str) -> tuple[bool, str]:
    key = (key or "").strip()
    if not key:
        return False, "Configurez votre clé API dans Paramètres avant d'analyser des documents."
    if not key.startswith("sk-"):
        return False, "La clé API Aristote doit commencer par « sk- »."
    return True, ""


class Parametre:
    # Chemin du fichier caché pour stocker le CodeConnexionAPI
    @staticmethod
    def _getConfigFile():
        config_dir = Path.home() / ".app_config"
        config_dir.mkdir(exist_ok=True)
        return config_dir / "config.json"

    CONFIG_FILE = _getConfigFile()

    def __init__(self, w):
        self.window = w
        self.window.setWindowTitle("Liste des paramètres")
        self.chargerCodeConnexionAPI()

    def chargerCodeConnexionAPI(self):
        self.window.CodeConnexionAPI.setText(_read_api_key())

    def sauvegarderCodeConnexionAPI(self):
        clef_path = _get_clef_path()
        clef_path.parent.mkdir(parents=True, exist_ok=True)
        clef_path.write_text(self.window.CodeConnexionAPI.text(), encoding="utf-8")

    def getCodeConnexionAPI(self):
        """Retourne le CodeConnexionAPI"""
        return self.window.CodeConnexionAPI.text()

    def retour(self) -> bool:
        ok, message = validate_api_key(self.window.CodeConnexionAPI.text())
        if not ok:
            QtWidgets.QMessageBox.warning(self.window, "Clé API manquante", message)
            return False
        self.sauvegarderCodeConnexionAPI()
        return True


def getCodeConnexionAPI():
    return _read_api_key()


def avertir_si_clef_api_manquante(parent=None) -> bool:
    """Affiche un avertissement si aucune clé API n'est configurée."""
    if has_api_key():
        return True
    QtWidgets.QMessageBox.warning(
        parent,
        "Clé API manquante",
        "Configurez votre clé API dans Paramètres avant d'analyser des documents.",
    )
    return False