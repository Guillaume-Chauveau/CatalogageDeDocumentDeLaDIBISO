"""Path helpers for normal runs and PyInstaller builds."""

import os
import sys


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


def get_scan_directories(selected_dir=None) -> list[str]:
    """Return the accessible scan directories: always Scan, plus one optional extra folder."""
    directories = [get_default_scan_dir()]

    if not selected_dir:
        return directories

    if os.path.isabs(selected_dir):
        resolved_dir = os.path.abspath(selected_dir)
    else:
        resolved_dir = os.path.abspath(get_data_dir(selected_dir))

    if resolved_dir != directories[0] and resolved_dir not in directories:
        directories.append(resolved_dir)

    return directories
