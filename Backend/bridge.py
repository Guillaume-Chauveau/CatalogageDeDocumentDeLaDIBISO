"""
Pont entre l'interface graphique et le pipeline OCR (pipeline + convert_json_to_txt4).

- mode « image »            : équivalent CLI --image (un fichier, un seul modèle)
- mode « batch »             : équivalent CLI --batch (dossier entier, un seul modèle)
- mode « image consensus »  : deux modèles vision + arbitrage (consensus_pipeline)
"""

import json
import sys
from pathlib import Path

_BACKEND_DIR = Path(__file__).resolve().parent
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from pipeline import AristoteDocumentAnalyzer, process_batch, API_BASE_URL
from convert_json_to_txt4 import build_lines
from consensus_pipeline import merge_results, enrich_consensus
from openai import OpenAI

APP_ROOT = _BACKEND_DIR.parent
JSON_OUTPUT_DIR = APP_ROOT / "outputs" / "aristote_results"
CONSENSUS_OUTPUT_DIR = APP_ROOT / "outputs" / "consensus_results"
LLM_OUTPUT_DIR = APP_ROOT / "LLMOutput"
DOC_DIR = APP_ROOT / "Doc"


def get_analyzer(api_key: str, model: str = None, enrichment_model: str = None) -> AristoteDocumentAnalyzer:
    key = (api_key or "").strip()
    if not key:
        raise ValueError(
            "Clé API non configurée. Renseignez-la dans Paramètres avant d'analyser des documents."
        )
    kwargs = {"base_url": API_BASE_URL, "api_key": key}
    if model:
        kwargs["model"] = model
    if enrichment_model:
        kwargs["enrichment_model"] = enrichment_model
    return AristoteDocumentAnalyzer(**kwargs)


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


# --- Mode mono-modèle (existant, inchangé) ---


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


def process_image_batch_consensus(
    input_dir: str,
    api_key: str,
    model_a: str = "gemma-4-31b",
    model_b: str = "qwen-3.6-35b-instruct",
    text_model: str = "gpt-oss-120b",
) -> list[str]:
    """Traite un dossier d'images en mode consensus (--batch). Retourne la liste des stems traités."""
    input_path = Path(input_dir)
    if not input_path.is_dir():
        raise NotADirectoryError(f"Dossier introuvable : {input_dir}")

    image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}
    image_files = sorted(
        f for f in input_path.iterdir() if f.suffix.lower() in image_extensions
    )

    processed = []
    for image_file in image_files:
        try:
            stem = process_single_image_consensus(
                str(image_file),
                api_key,
                model_a=model_a,
                model_b=model_b,
                text_model=text_model,
            )
            processed.append(stem)
        except Exception as exc:
            print(f"Erreur lors du traitement de {image_file.name} : {exc}")
            continue

    return processed


# --- Mode consensus (deux modèles vision + arbitrage) ---


def process_single_image_consensus(
    image_path: str,
    api_key: str,
    model_a: str,
    model_b: str,
    text_model: str = "gpt-oss-120b",
    force: bool = False,
) -> str:
    """Traite une image avec les deux modèles vision + arbitrage/enrichissement consensus."""
    path = Path(image_path)
    if not path.is_file():
        raise FileNotFoundError(f"Image introuvable : {image_path}")

    CONSENSUS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = CONSENSUS_OUTPUT_DIR / f"{path.stem}.json"
    if json_path.exists() and not force:
        print(f"Fichier {path.name} déjà traité (consensus). Ignoré.")
        return path.stem

    analyzer_a = get_analyzer(api_key, model=model_a, enrichment_model=text_model)
    analyzer_b = get_analyzer(api_key, model=model_b, enrichment_model=text_model)
    client = OpenAI(base_url=API_BASE_URL, api_key=(api_key or "").strip())

    result_a = analyzer_a.process_image(str(path))
    result_b = analyzer_b.process_image(str(path))

    if "error" in (result_a.get("metadata", {}) or {}) or "error" in (result_b.get("metadata", {}) or {}):
        raise RuntimeError(
            f"Échec d'au moins un des deux modèles sur {path.name} "
            f"({model_a}: {result_a.get('metadata', {}).get('error')}, "
            f"{model_b}: {result_b.get('metadata', {}).get('error')})"
        )

    consensus = merge_results(result_a, result_b, model_a, model_b, client, text_model)
    enrich_consensus(analyzer_a, consensus["metadata"], consensus["consensus_detail"])
    consensus["confidence_scores"] = consensus["consensus_detail"]
    consensus["image_filename"] = path.name

    CONSENSUS_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    json_path = CONSENSUS_OUTPUT_DIR / f"{path.stem}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(consensus, f, indent=2, ensure_ascii=False)

    _write_txt_from_result(consensus, path.stem)
    return path.stem