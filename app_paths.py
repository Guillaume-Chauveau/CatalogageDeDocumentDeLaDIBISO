"""Path helpers for normal runs and PyInstaller builds."""

import os
import sys
import json


APP_VERSION = "v1"
_SCAN_DIRECTORIES = []


def bootstrap_scan_directories() -> list[str]:
    """Load persisted scan directories from disk on startup."""
    global _SCAN_DIRECTORIES
    if _SCAN_DIRECTORIES:
        return list(_SCAN_DIRECTORIES)

    config_path = _get_config_path()
    if not os.path.exists(config_path):
        try:
            with open(config_path, "w", encoding="utf-8") as handle:
                json.dump([], handle, ensure_ascii=False, indent=2)
        except OSError:
            pass

    persisted = _load_saved_scan_directories()
    _SCAN_DIRECTORIES = list(persisted)
    return list(_SCAN_DIRECTORIES)


def _get_config_path() -> str:
    versioned_name = f"scan_directories_{APP_VERSION}.json"
    return os.path.join(get_project_dir(), versioned_name)


def _load_saved_scan_directories() -> list[str]:
    config_path = _get_config_path()
    if not os.path.exists(config_path):
        return []
    try:
        with open(config_path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
            if isinstance(data, list):
                return [str(path) for path in data if str(path)]
    except (OSError, json.JSONDecodeError):
        return []
    return []


def _save_scan_directories() -> None:
    config_path = _get_config_path()
    try:
        existing = _load_saved_scan_directories()
        merged = list(existing)
        for directory in _SCAN_DIRECTORIES:
            if directory not in merged:
                merged.append(directory)
        with open(config_path, "w", encoding="utf-8") as handle:
            json.dump(merged, handle, ensure_ascii=False, indent=2)
    except OSError:
        pass


def is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def get_project_dir() -> str:
    return os.path.dirname(os.path.abspath(__file__))


def get_resource_dir() -> str:
    """Read-only bundled assets (UI, Image, champs_scientifiques.txt)."""
    if is_frozen() and hasattr(sys, "_MEIPASS"):
        return os.path.abspath(sys._MEIPASS)
    return get_project_dir()


def get_exe_dir() -> str:
    """Directory of the running app (project root in dev, folder of the .exe when frozen)."""
    if is_frozen():
        return os.path.dirname(os.path.abspath(sys.executable))
    return get_project_dir()


def get_data_dir(name: str) -> str:
    """Writable working folders: Doc, Scan, LLMOutput, Sortie."""
    path = os.path.join(get_exe_dir(), name)
    os.makedirs(path, exist_ok=True)
    return path


def get_default_scan_dir() -> str:
    return get_data_dir("Scan")


def clear_scan_directories() -> None:
    global _SCAN_DIRECTORIES
    _SCAN_DIRECTORIES = []


def add_scan_directory(directory) -> None:
    global _SCAN_DIRECTORIES
    resolved_dir = _resolve_scan_directory(directory)
    if resolved_dir and resolved_dir not in _SCAN_DIRECTORIES:
        _SCAN_DIRECTORIES.append(resolved_dir)
        _save_scan_directories()


def _resolve_scan_directory(directory) -> str | None:
    if not directory:
        return None
    if os.path.isabs(directory):
        return os.path.abspath(directory)
    return os.path.abspath(get_data_dir(directory))


def get_scan_directories(selected_dirs=None) -> list[str]:
    """Return all known scan directories, always starting with Scan and then any added absolute paths."""
    directories = [get_default_scan_dir()]
    global _SCAN_DIRECTORIES

    bootstrap_scan_directories()

    if not selected_dirs:
        selected_dirs = []
    elif isinstance(selected_dirs, (str, os.PathLike)):
        selected_dirs = [selected_dirs]

    for directory in list(selected_dirs) + list(_SCAN_DIRECTORIES):
        resolved_dir = _resolve_scan_directory(directory)
        if not resolved_dir or resolved_dir == directories[0] or resolved_dir in directories:
            continue
        directories.append(resolved_dir)

    return directories
