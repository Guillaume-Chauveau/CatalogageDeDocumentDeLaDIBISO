"""
Pont entre l'interface graphique et le pipeline OCR (gemma_gpt + convert_json_to_txt4).

- mode « image »  : équivalent CLI --image (un fichier)
- mode « batch »  : équivalent CLI --batch (dossier entier)
"""

import json
import sys
from pathlib import Path

_BACKEND_DIR = Path(__file__).resolve().parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from gemma_gpt import AristoteDocumentAnalyzer, process_batch, API_BASE_URL
from convert_json_to_txt4 import build_lines

APP_ROOT = _BACKEND_DIR.parent
JSON_OUTPUT_DIR = APP_ROOT / "outputs" / "aristote_results"
LLM_OUTPUT_DIR = APP_ROOT / "LLMOutput"
DOC_DIR = APP_ROOT / "Doc"


def get_analyzer(api_key: str) -> AristoteDocumentAnalyzer:
    key = (api_key or "").strip()
    if not key:
        raise ValueError(
            "Clé API non configurée. Renseignez-la dans Paramètres avant d'analyser des documents."
        )
    return AristoteDocumentAnalyzer(base_url=API_BASE_URL, api_key=key)


def _write_txt_from_result(result: dict, stem: str) -> None:
    lines = build_lines(result)
    content = "\n".join(lines) + "\n"
    for dir_path in (LLM_OUTPUT_DIR, DOC_DIR):
        dir_path.mkdir(parents=True, exist_ok=True)
        with open(dir_path / f"{stem}.txt", "w", encoding="utf-8") as f:
            f.write(content)


def _convert_json_to_txt(json_path: Path, stem: str) -> None:
    with open(json_path, "r", encoding="utf-8") as f:
        result = json.load(f)
    _write_txt_from_result(result, stem)


def process_single_image(image_path: str, api_key: str) -> str:
    """Traite une image (--image). Retourne le stem du fichier."""
    path = Path(image_path)
    if not path.is_file():
        raise FileNotFoundError(f"Image introuvable : {image_path}")

    analyzer = get_analyzer(api_key)
    result = analyzer.process_image(str(path))

    JSON_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = JSON_OUTPUT_DIR / f"{path.stem}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    _write_txt_from_result(result, path.stem)
    return path.stem


def process_image_batch(input_dir: str, api_key: str) -> list[str]:
    """Traite un dossier d'images (--batch). Retourne la liste des stems traités."""
    input_path = Path(input_dir)
    if not input_path.is_dir():
        raise NotADirectoryError(f"Dossier introuvable : {input_dir}")

    analyzer = get_analyzer(api_key)
    JSON_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    process_batch(analyzer, input_path, JSON_OUTPUT_DIR)

    image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}
    stems = sorted(
        f.stem for f in input_path.iterdir() if f.suffix.lower() in image_extensions
    )

    processed = []
    for stem in stems:
        json_path = JSON_OUTPUT_DIR / f"{stem}.json"
        if not json_path.exists():
            continue
        _convert_json_to_txt(json_path, stem)
        processed.append(stem)
    return processed
