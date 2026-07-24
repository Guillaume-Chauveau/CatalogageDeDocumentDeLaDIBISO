import app_paths


def test_get_scan_directories_includes_default_and_optional_extra(tmp_path, monkeypatch):
    monkeypatch.setattr(app_paths, "get_exe_dir", lambda: str(tmp_path))

    default_dir = tmp_path / "Scan"
    default_dir.mkdir()
    extra_dir = tmp_path / "AutreScan"
    extra_dir.mkdir()

    directories = app_paths.get_scan_directories(str(extra_dir))

    assert directories == [str(default_dir), str(extra_dir)]


def test_get_scan_directories_deduplicates_default_and_selected_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(app_paths, "get_exe_dir", lambda: str(tmp_path))

    default_dir = tmp_path / "Scan"
    default_dir.mkdir()

    directories = app_paths.get_scan_directories(str(default_dir))

    assert directories == [str(default_dir)]
