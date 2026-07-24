from types import SimpleNamespace
import json
import os
import sys
import types

import app_paths


class StubWindow:
    def __init__(self):
        self.enabled = True
        self.listWidget = SimpleNamespace(clear=lambda: None, addItem=lambda *args, **kwargs: None)
        self.listWidget.enabled = True
        self.listWidget.setEnabled = lambda value: setattr(self.listWidget, "enabled", value)
        self.AfficheDossier = SimpleNamespace(setText=lambda value: None)
        self.AjouterUnFichier = SimpleNamespace(setEnabled=lambda value: None)
        self.ChoisirUnNouveauDossierDeBase = SimpleNamespace(setEnabled=lambda value: None)
        self.Reactualiser = SimpleNamespace(setEnabled=lambda value: None)
        self.VoirFini = SimpleNamespace(isChecked=lambda: False)

    def setWindowTitle(self, title):
        self.title = title

    def setEnabled(self, value):
        self.enabled = value


def test_get_scan_directories_includes_default_and_optional_extra(tmp_path, monkeypatch):
    monkeypatch.setattr(app_paths, "get_exe_dir", lambda: str(tmp_path))
    app_paths._SCAN_DIRECTORIES = []
    if os.path.exists(app_paths._get_config_path()):
        os.remove(app_paths._get_config_path())

    default_dir = tmp_path / "Scan"
    default_dir.mkdir()
    extra_dir = tmp_path / "AutreScan"
    extra_dir.mkdir()

    directories = app_paths.get_scan_directories(str(extra_dir))

    assert directories == [str(default_dir), str(extra_dir)]


def test_get_scan_directories_deduplicates_default_and_selected_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(app_paths, "get_exe_dir", lambda: str(tmp_path))
    app_paths._SCAN_DIRECTORIES = []
    if os.path.exists(app_paths._get_config_path()):
        os.remove(app_paths._get_config_path())

    default_dir = tmp_path / "Scan"
    default_dir.mkdir()

    directories = app_paths.get_scan_directories(str(default_dir))

    assert directories == [str(default_dir)]


def test_add_scan_directory_keeps_multiple_added_paths(tmp_path, monkeypatch):
    monkeypatch.setattr(app_paths, "get_exe_dir", lambda: str(tmp_path))
    app_paths.clear_scan_directories()

    first_dir = tmp_path / "Scan"
    first_dir.mkdir()
    second_dir = tmp_path / "AutreScan"
    second_dir.mkdir()
    third_dir = tmp_path / "EncoreUnAutre"
    third_dir.mkdir()

    app_paths.add_scan_directory(second_dir)
    app_paths.add_scan_directory(third_dir)

    directories = app_paths.get_scan_directories([second_dir, third_dir])

    assert directories[0] == str(first_dir)
    assert directories[1:] == [str(second_dir), str(third_dir)]


def test_added_scan_directories_are_persisted_and_reloaded(tmp_path, monkeypatch):
    monkeypatch.setattr(app_paths, "get_exe_dir", lambda: str(tmp_path))
    app_paths.clear_scan_directories()

    extra_dir = tmp_path / "DossierPersiste"
    extra_dir.mkdir()

    app_paths.add_scan_directory(extra_dir)

    app_paths._SCAN_DIRECTORIES = []
    directories = app_paths.get_scan_directories()

    assert directories[-1] == str(extra_dir)


def test_bootstrap_loads_saved_scan_directories_from_config(tmp_path, monkeypatch):
    monkeypatch.setattr(app_paths, "get_exe_dir", lambda: str(tmp_path))
    config_path = app_paths._get_config_path()
    app_paths.clear_scan_directories()

    extra_dir = tmp_path / "DossierAuDemarrage"
    extra_dir.mkdir()

    with open(config_path, "w", encoding="utf-8") as handle:
        json.dump([str(extra_dir)], handle)

    app_paths._SCAN_DIRECTORIES = []
    app_paths.bootstrap_scan_directories()

    assert app_paths._SCAN_DIRECTORIES == [str(extra_dir)]


def test_bootstrap_creates_versioned_config_file_on_first_launch(tmp_path, monkeypatch):
    monkeypatch.setattr(app_paths, "get_exe_dir", lambda: str(tmp_path))
    monkeypatch.setattr(app_paths, "APP_VERSION", "v2")
    app_paths.clear_scan_directories()

    if os.path.exists(app_paths._get_config_path()):
        os.remove(app_paths._get_config_path())

    app_paths.bootstrap_scan_directories()

    assert os.path.exists(app_paths._get_config_path())
    assert app_paths._load_saved_scan_directories() == []


def test_processing_ui_disables_catalogue_interactions(tmp_path, monkeypatch):
    monkeypatch.setattr(app_paths, "get_exe_dir", lambda: str(tmp_path))

    fake_qtwidgets = types.SimpleNamespace(
        QListWidgetItem=lambda *args, **kwargs: None,
        QStyle=types.SimpleNamespace(StandardPixmap=types.SimpleNamespace(SP_MessageBoxWarning=None)),
        QApplication=types.SimpleNamespace(processEvents=lambda: None),
        QMessageBox=types.SimpleNamespace(warning=lambda *args, **kwargs: None, information=lambda *args, **kwargs: None, critical=lambda *args, **kwargs: None),
        QFileDialog=types.SimpleNamespace(FileMode=types.SimpleNamespace(ExistingFiles=None, Directory=None), ViewMode=types.SimpleNamespace(List=None)),
    )
    fake_qtgui = types.SimpleNamespace(QIcon=lambda *args, **kwargs: None, QCursor=lambda *args, **kwargs: None)
    fake_qtcore = types.SimpleNamespace(
        QThread=type("QThread", (), {}),
        Signal=lambda *args, **kwargs: None,
        Qt=types.SimpleNamespace(CursorShape=types.SimpleNamespace(WaitCursor=None, ArrowCursor=None), WindowModality=types.SimpleNamespace(WindowModal=None)),
    )

    pyside_module = types.ModuleType("PySide6")
    setattr(pyside_module, "QtWidgets", fake_qtwidgets)
    setattr(pyside_module, "QtGui", fake_qtgui)
    setattr(pyside_module, "QtCore", fake_qtcore)
    sys.modules["PySide6"] = pyside_module
    sys.modules["PySide6.QtWidgets"] = fake_qtwidgets
    sys.modules["PySide6.QtGui"] = fake_qtgui
    sys.modules["PySide6.QtCore"] = fake_qtcore

    fake_backend = types.ModuleType("Backend.bridge")
    fake_backend.process_single_image = lambda *args, **kwargs: None
    fake_backend.process_single_image_consensus = lambda *args, **kwargs: None
    fake_backend.process_image_batch = lambda *args, **kwargs: None
    fake_backend.process_image_batch_consensus = lambda *args, **kwargs: None
    sys.modules["Backend.bridge"] = fake_backend

    import ListeAFinir

    window = StubWindow()
    catalogue = ListeAFinir.ListeAFinir(window, "Scan")

    catalogue._set_processing_ui(True)

    assert window.enabled is False
    assert getattr(window.listWidget, "enabled", True) is False
