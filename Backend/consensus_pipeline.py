"""
consensus_pipeline.py

Fait collaborer DEUX modèles VISION (typiquement Gemma et Qwen) sur la même
image, champ par champ, avec un mécanisme de consensus/arbitrage :

  1. Passe 1 x2 : chaque modèle vision extrait indépendamment les métadonnées
     bibliographiques (via AristoteDocumentAnalyzer.process_image).
  2. Comparaison champ par champ (accord / désaccord + arbitrage texte).
  3. Passe d'enrichissement UNIQUE, relancée sur les champs FUSIONNÉS
     (post-consensus), pour produire authors_parsed / scientific_field /
     romanization de façon cohérente avec les valeurs retenues — plutôt que
     de recopier ces champs depuis un seul des deux runs (qui auraient pu
     être calculés sur un "authors" différent de celui finalement choisi).

Sortie, pour chaque image :

    <output_dir>/<model_a>/<stem>.json       <- résultat brut modèle A
    <output_dir>/<model_b>/<stem>.json       <- résultat brut modèle B
    <output_dir>/consensus/<stem>.json       <- métadonnées fusionnées
                                                 + enrichissement + détail
                                                 accord/arbitrage

Usage :
    python consensus_pipeline.py \
        --input-dir ./mes_images \
        --output-dir ./outputs/consensus \
        --model-a gemma-4-31b \
        --model-b qwen-3.6-35b-instruct \
        --text-model gpt-oss-120b \
        --base-url https://llm.aristote.education/v1 \
        --api-key "TA_CLE"

Nécessite `pipeline.py` (classe AristoteDocumentAnalyzer) dans le même
dossier ou sur le PYTHONPATH.
"""

import argparse
import difflib
import inspect
import json
import logging
import re
import time
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from openai import OpenAI

from pipeline import AristoteDocumentAnalyzer  # ton fichier pipeline.py

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}

# Champs produits par la passe 1 (vision) uniquement — ceux qu'on compare
# entre les deux modèles. Les champs d'enrichissement (authors_parsed,
# scientific_field, romanization) ne sont PAS comparés ici : ils sont
# recalculés une seule fois après fusion (cf. enrich_consensus).
SCALAR_FIELDS = [
    "title", "title_complement", "volume_number", "authors", "author_titles",
    "translators", "illustrators", "prefaciers", "editors",
    "edition", "collection", "illustrations", "date",
]
STRICT_FIELDS = ["language", "script"]
LIST_FIELDS = ["publishers"]

FUZZY_MATCH_THRESHOLD = 0.92
CONFLICT_CONFIDENCE_PENALTY = 0.5

# Champs texte scalaires envoyés à la passe d'enrichissement (même liste que
# dans pipeline.py, pour rester synchro avec le schéma attendu par le prompt).
ENRICHMENT_SCALAR_KEYS = [
    "title", "title_complement", "volume_number", "authors", "translators",
    "illustrators", "prefaciers", "editors", "edition", "collection",
    "illustrations", "language", "script",
]
ROMANIZATION_SCALAR_KEYS = [
    "title", "title_complement", "volume_number", "authors", "translators",
    "illustrators", "prefaciers", "editors", "edition", "collection",
    "illustrations",
]


# Détection de la signature du constructeur


_INIT_PARAMS = set(inspect.signature(AristoteDocumentAnalyzer.__init__).parameters)
if "ocr_model" in _INIT_PARAMS and "text_model" in _INIT_PARAMS:
    _VISION_PARAM, _TEXT_PARAM = "ocr_model", "text_model"
elif "model" in _INIT_PARAMS and "enrichment_model" in _INIT_PARAMS:
    _VISION_PARAM, _TEXT_PARAM = "model", "enrichment_model"
else:
    raise RuntimeError(
        "Impossible de détecter les paramètres du constructeur de "
        "AristoteDocumentAnalyzer dans pipeline.py."
    )
logger.info(f"Signature détectée dans pipeline.py : ({_VISION_PARAM}, {_TEXT_PARAM})")


# Normalisation / comparaison de champs


def normalize_text(s: str) -> str:
    s = s.strip().lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"\s+", " ", s)
    return s


def text_similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, normalize_text(a), normalize_text(b)).ratio()


CONTAINMENT_FIELDS = {"title", "title_complement"}
CONTAINMENT_MIN_RATIO = 0.6  # le plus court doit couvrir au moins 60% du plus long


def is_containment(value_a: str, value_b: str) -> bool:
    """
    True si l'une des deux valeurs est un préfixe/sous-chaîne quasi complète
    de l'autre. Cas typique : un modèle vision tronque le titre ou le
    sous-titre (page dense, texte petit) alors que l'autre le lit en entier.
    Ce n'est PAS un vrai désaccord de contenu, juste un problème de
    complétude — inutile (et risqué) de le confier à l'arbitrage texte, qui
    n'a pas accès à l'image et pourrait préférer la version tronquée.
    """
    na, nb = normalize_text(value_a), normalize_text(value_b)
    if not na or not nb or na == nb:
        return False
    shorter, longer = (na, nb) if len(na) <= len(nb) else (nb, na)
    if shorter not in longer:
        return False
    return len(shorter) / len(longer) >= CONTAINMENT_MIN_RATIO


def _as_text(value: Any) -> str:
    """
    Coercion défensive : un champ censé être scalaire (ex: "authors") peut
    arriver ici sous forme de liste si un run plus ancien (avant correctif
    dans pipeline.py) a été rejoué, ou si un modèle a renvoyé un type
    inattendu. On ramène toujours à une chaîne "; "-séparée plutôt que de
    planter sur .strip()/.lower().
    """
    if isinstance(value, list):
        return " ; ".join(str(v).strip() for v in value if str(v).strip())
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False)
    return value or ""


def scalar_fields_agree(value_a: Any, value_b: Any) -> bool:
    a, b = _as_text(value_a).strip(), _as_text(value_b).strip()
    if a == "" and b == "":
        return True
    if a == "" or b == "":
        return False
    return text_similarity(a, b) >= FUZZY_MATCH_THRESHOLD


def strict_fields_agree(value_a: str, value_b: str) -> bool:
    return normalize_text(value_a or "") == normalize_text(value_b or "")


def normalize_publisher_entry(entry: Dict[str, str]) -> Tuple[str, str]:
    return (normalize_text(entry.get("publisher", "")), normalize_text(entry.get("place", "")))


def publishers_agree(list_a: List[Dict[str, str]], list_b: List[Dict[str, str]]) -> bool:
    set_a = {normalize_publisher_entry(e) for e in (list_a or [])}
    set_b = {normalize_publisher_entry(e) for e in (list_b or [])}
    return set_a == set_b


# Arbitrage des désaccords (modèle texte, sans image)


def arbitrate_field(
    client: OpenAI,
    text_model: str,
    field_name: str,
    value_a: Any,
    model_a_name: str,
    value_b: Any,
    model_b_name: str,
    context: Dict[str, Any],
) -> Dict[str, Any]:
    prompt = (
        "Tu es un bibliothécaire expert en catalogage patrimonial (norme ISBD). "
        "Deux systèmes de lecture automatique ont extrait des valeurs DIFFÉRENTES "
        f"pour le champ \"{field_name}\" d'un même ouvrage. Tu dois choisir laquelle "
        "des deux valeurs est la plus vraisemblablement correcte, à partir du "
        "contexte fourni.\n\n"
        "IMPORTANT : tu n'as pas accès à l'image source. Tu dois choisir "
        "EXCLUSIVEMENT entre le candidat A et le candidat B, sans jamais "
        "proposer ou halluciner une troisième valeur, même si aucun des deux "
        "ne te semble pleinement satisfaisant.\n\n"
        + (
            "RÈGLE SPÉCIFIQUE AUX TITRES/SOUS-TITRES : si les deux candidats se "
            "ressemblent mais qu'un des deux semble plus DÉVELOPPÉ, plus LONG ou "
            "plus DÉTAILLÉ que l'autre (l'un contient une clause, une énumération "
            "ou une fin de phrase absente de l'autre), privilégie SYSTÉMATIQUEMENT "
            "le candidat le plus complet : un titre extrait par un système de "
            "lecture automatique est presque toujours tronqué par manque de "
            "lisibilité, jamais rallongé par invention. Un candidat plus court "
            "n'est préférable que s'il corrige une erreur de lecture manifeste "
            "(mot clairement mal reconnu), pas simplement parce qu'il paraît plus "
            "sobre ou mieux formé stylistiquement.\n\n"
            if field_name in ("title", "title_complement") else ""
        )
        + f"Contexte (autres champs déjà confirmés par les deux systèmes) :\n"
        f"{json.dumps(context, ensure_ascii=False)}\n\n"
        f"Candidat A ({model_a_name}) pour \"{field_name}\" : {json.dumps(value_a, ensure_ascii=False)}\n"
        f"Candidat B ({model_b_name}) pour \"{field_name}\" : {json.dumps(value_b, ensure_ascii=False)}\n\n"
        "Réponds UNIQUEMENT avec ce JSON, sans markdown ni texte autour :\n"
        "{\"chosen\": \"A\" ou \"B\", \"note\": \"justification en une courte phrase\"}"
    )

    try:
        response = client.chat.completions.create(
            model=text_model,
            max_tokens=3500,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = (response.choices[0].message.content or "").strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(raw)
        chosen = parsed.get("chosen", "A").strip().upper()
        if chosen not in ("A", "B"):
            chosen = "A"
        return {"chosen": chosen, "note": parsed.get("note", "")}
    except Exception as e:
        logger.warning(f"Échec de l'arbitrage pour le champ '{field_name}': {e}. Repli sur A par défaut.")
        return {"chosen": "A", "note": f"arbitrage échoué ({e}), repli par défaut sur le candidat A"}


# Fusion des deux résultats (passe 1 uniquement)


def get_field_confidence(confidence_scores: Dict[str, Any], field: str) -> Optional[float]:
    entry = (confidence_scores or {}).get(field)
    if isinstance(entry, dict):
        return entry.get("confidence")
    return None


def merge_results(
    result_a: Dict[str, Any],
    result_b: Dict[str, Any],
    model_a_name: str,
    model_b_name: str,
    client: OpenAI,
    text_model: str,
) -> Dict[str, Any]:
    meta_a = result_a.get("metadata", {}) or {}
    meta_b = result_b.get("metadata", {}) or {}
    conf_a = result_a.get("confidence_scores", {}) or {}
    conf_b = result_b.get("confidence_scores", {}) or {}

    merged_metadata: Dict[str, Any] = {}
    consensus_detail: Dict[str, Any] = {}

    agreed_context: Dict[str, Any] = {}
    pending_conflicts: List[str] = []

    def process_scalar(field: str, agree_fn) -> None:
        val_a, val_b = _as_text(meta_a.get(field, "")), _as_text(meta_b.get(field, ""))
        if agree_fn(val_a, val_b):
            chosen_value = val_a if val_a else val_b
            c_a, c_b = get_field_confidence(conf_a, field), get_field_confidence(conf_b, field)
            candidates = [c for c in (c_a, c_b) if c is not None]
            merged_metadata[field] = chosen_value
            consensus_detail[field] = {
                "agreement": True,
                f"value_{model_a_name}": val_a,
                f"value_{model_b_name}": val_b,
                "chosen_value": chosen_value,
                "confidence": max(candidates) if candidates else None,
            }
            agreed_context[field] = chosen_value
        elif field in CONTAINMENT_FIELDS and is_containment(val_a, val_b):
            # Désaccord apparent mais probable troncature d'un des deux
            # modèles : on garde la version la plus longue/complète plutôt
            # que de risquer un arbitrage aveugle qui choisirait la version
            # tronquée.
            chosen_value = val_a if len(val_a) >= len(val_b) else val_b
            c_a, c_b = get_field_confidence(conf_a, field), get_field_confidence(conf_b, field)
            candidates = [c for c in (c_a, c_b) if c is not None]
            merged_metadata[field] = chosen_value
            consensus_detail[field] = {
                "agreement": True,
                "resolution": "containment_heuristic_kept_longer",
                f"value_{model_a_name}": val_a,
                f"value_{model_b_name}": val_b,
                "chosen_value": chosen_value,
                "confidence": min(candidates) if candidates else None,
            }
            agreed_context[field] = chosen_value
        else:
            pending_conflicts.append(field)

    for field in SCALAR_FIELDS:
        process_scalar(field, scalar_fields_agree)
    for field in STRICT_FIELDS:
        process_scalar(field, strict_fields_agree)

    pubs_a, pubs_b = meta_a.get("publishers", []), meta_b.get("publishers", [])
    if publishers_agree(pubs_a, pubs_b):
        chosen_pubs = pubs_a if pubs_a else pubs_b
        c_a, c_b = get_field_confidence(conf_a, "publishers"), get_field_confidence(conf_b, "publishers")
        candidates = [c for c in (c_a, c_b) if c is not None]
        merged_metadata["publishers"] = chosen_pubs
        consensus_detail["publishers"] = {
            "agreement": True,
            f"value_{model_a_name}": pubs_a,
            f"value_{model_b_name}": pubs_b,
            "chosen_value": chosen_pubs,
            "confidence": max(candidates) if candidates else None,
        }
        agreed_context["publishers"] = chosen_pubs
    else:
        pending_conflicts.append("publishers")

    for field in pending_conflicts:
        val_a = meta_a.get(field, "" if field != "publishers" else [])
        val_b = meta_b.get(field, "" if field != "publishers" else [])

        arbitration = arbitrate_field(
            client=client,
            text_model=text_model,
            field_name=field,
            value_a=val_a,
            model_a_name=model_a_name,
            value_b=val_b,
            model_b_name=model_b_name,
            context=agreed_context,
        )

        chosen_value = val_a if arbitration["chosen"] == "A" else val_b
        c_a, c_b = get_field_confidence(conf_a, field), get_field_confidence(conf_b, field)
        candidates = [c for c in (c_a, c_b) if c is not None]
        base_confidence = min(candidates) if candidates else None
        final_confidence = (
            round(base_confidence * CONFLICT_CONFIDENCE_PENALTY, 4)
            if base_confidence is not None else None
        )

        merged_metadata[field] = chosen_value
        consensus_detail[field] = {
            "agreement": False,
            f"value_{model_a_name}": val_a,
            f"value_{model_b_name}": val_b,
            "chosen_value": chosen_value,
            "arbitration_chosen": arbitration["chosen"],
            "arbitration_note": arbitration["note"],
            "confidence": final_confidence,
        }

    return {
        "metadata": merged_metadata,
        "consensus_detail": consensus_detail,
        "n_fields_compared": len(SCALAR_FIELDS) + len(STRICT_FIELDS) + len(LIST_FIELDS),
        "n_agreements": sum(1 for v in consensus_detail.values() if v["agreement"]),
        "n_conflicts_arbitrated": sum(1 for v in consensus_detail.values() if not v["agreement"]),
    }


# Enrichissement post-consensus (authors_parsed / scientific_field / romanization)


def enrich_consensus(
    analyzer: AristoteDocumentAnalyzer,
    merged_metadata: Dict[str, Any],
    consensus_detail: Dict[str, Any],
) -> None:
    """
    Relance la passe 2 (enrichissement) sur les champs FUSIONNÉS
    (post-consensus/arbitrage), et injecte authors_parsed / scientific_field /
    romanization dans merged_metadata + les scores de confiance correspondants
    dans consensus_detail — pour que le résultat final soit consommable par
    build_lines() exactement comme un résultat process_image() classique.

    On ne peut pas recopier authors_parsed/scientific_field depuis l'un des
    deux runs : ils ont potentiellement été calculés sur un "authors" (ou un
    "title"/"collection") différent de celui finalement retenu par le
    consensus. Il faut les recalculer sur les valeurs consensus.
    """
    script_value = str(merged_metadata.get("script") or "").strip().lower()
    is_non_latin = "non" in script_value and "latin" in script_value

    fields_for_enrichment = {
        k: merged_metadata.get(k, [] if k == "publishers" else "")
        for k in ENRICHMENT_SCALAR_KEYS + ["publishers"]
    }

    has_exploitable_content = bool(merged_metadata.get("title")) or bool(merged_metadata.get("authors"))
    if not has_exploitable_content:
        merged_metadata["scientific_field"] = ""
        merged_metadata["authors_parsed"] = []
        merged_metadata["romanization"] = {}
        return

    try:
        enrich_raw, enrich_token_logprobs, enrich_logprobs_error = analyzer._generate_enrichment(
            fields=fields_for_enrichment, include_romanization=is_non_latin,
        )
        enrich_metadata = analyzer._parse_enrichment_response(
            enrich_raw, include_romanization=is_non_latin
        ) or {}

        merged_metadata["scientific_field"] = enrich_metadata.get("scientific_field", "")
        merged_metadata["authors_parsed"] = enrich_metadata.get("authors_parsed", [])
        merged_metadata["romanization"] = (
            enrich_metadata.get("romanization", {}) if is_non_latin else {}
        )

        if enrich_token_logprobs is not None:
            spans, ref_text = analyzer._build_spans_and_reference(enrich_token_logprobs, enrich_raw)

            enrich_conf = analyzer._score_object_scalar_fields(ref_text, spans, ["scientific_field"])
            enrich_conf["authors_parsed"] = analyzer._score_list_field(
                ref_text, spans, "authors_parsed", ["raw", "given_name", "family_name"]
            )

            if is_non_latin:
                rom_conf = analyzer._score_object_scalar_fields(ref_text, spans, ROMANIZATION_SCALAR_KEYS)
                rom_conf["publishers"] = analyzer._score_publishers_field(ref_text, spans)
                enrich_conf["romanization"] = rom_conf

            consensus_detail.update(enrich_conf)
        elif enrich_logprobs_error:
            logger.warning(f"Enrichissement consensus sans logprobs : {enrich_logprobs_error}")

    except Exception as e:
        logger.error(f"Erreur lors de l'enrichissement post-consensus: {e}", exc_info=True)
        merged_metadata.setdefault("scientific_field", "")
        merged_metadata.setdefault("authors_parsed", [])
        merged_metadata.setdefault("romanization", {})


# Orchestration


def slugify(model_name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "_", model_name).strip("_")


def list_images(input_dir: Path) -> List[Path]:
    return sorted(f for f in input_dir.iterdir() if f.suffix.lower() in IMAGE_EXTENSIONS)


def process_single_image(
    image_file: Path,
    analyzer_a: AristoteDocumentAnalyzer,
    analyzer_b: AristoteDocumentAnalyzer,
    model_a_name: str,
    model_b_name: str,
    text_model: str,
    client: OpenAI,
    dir_a: Path,
    dir_b: Path,
    dir_consensus: Path,
) -> None:
    path_a, path_b = dir_a / f"{image_file.stem}.json", dir_b / f"{image_file.stem}.json"
    path_consensus = dir_consensus / f"{image_file.stem}.json"

    if path_consensus.exists():
        logger.info(f"  déjà traité, ignoré : {image_file.name}")
        return

    if path_a.exists():
        with open(path_a, "r", encoding="utf-8") as f:
            result_a = json.load(f)
    else:
        logger.info(f"  [{model_a_name}] traitement de {image_file.name}")
        result_a = analyzer_a.process_image(str(image_file))
        with open(path_a, "w", encoding="utf-8") as f:
            json.dump(result_a, f, indent=2, ensure_ascii=False)

    if path_b.exists():
        with open(path_b, "r", encoding="utf-8") as f:
            result_b = json.load(f)
    else:
        logger.info(f"  [{model_b_name}] traitement de {image_file.name}")
        result_b = analyzer_b.process_image(str(image_file))
        with open(path_b, "w", encoding="utf-8") as f:
            json.dump(result_b, f, indent=2, ensure_ascii=False)

    if "error" in (result_a.get("metadata", {}) or {}) or "error" in (result_b.get("metadata", {}) or {}):
        logger.warning(f"  {image_file.name} : erreur dans au moins un des deux runs, consensus ignoré.")
        merged = {
            "image_filename": image_file.name,
            "error": "au moins un des deux modèles a échoué sur cette image",
            f"error_{model_a_name}": (result_a.get("metadata", {}) or {}).get("error"),
            f"error_{model_b_name}": (result_b.get("metadata", {}) or {}).get("error"),
        }
        with open(path_consensus, "w", encoding="utf-8") as f:
            json.dump(merged, f, indent=2, ensure_ascii=False)
        return

    logger.info(f"  [{model_a_name} + {model_b_name}] fusion/arbitrage pour {image_file.name}")
    consensus = merge_results(result_a, result_b, model_a_name, model_b_name, client, text_model)

    logger.info(f"  enrichissement post-consensus pour {image_file.name}")
    enrich_consensus(analyzer_a, consensus["metadata"], consensus["consensus_detail"])

    # Alias pour que le résultat soit lisible directement par build_lines()
    # (qui attend "confidence_scores", pas "consensus_detail").
    consensus["confidence_scores"] = consensus["consensus_detail"]
    consensus["image_filename"] = image_file.name

    with open(path_consensus, "w", encoding="utf-8") as f:
        json.dump(consensus, f, indent=2, ensure_ascii=False)

    logger.info(
        f"    -> {consensus['n_agreements']} accords, "
        f"{consensus['n_conflicts_arbitrated']} conflits arbitrés"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Fait collaborer deux modèles vision via consensus/arbitrage champ par champ."
    )
    parser.add_argument("--input-dir", type=str, required=True)
    parser.add_argument("--output-dir", type=str, default="./outputs/consensus")
    parser.add_argument("--model-a", type=str, required=True, help="Premier modèle vision (ex: gemma-4-31b)")
    parser.add_argument("--model-b", type=str, required=True, help="Second modèle vision (ex: qwen-3.6-35b-instruct)")
    parser.add_argument("--text-model", type=str, default="gpt-oss-120b",
                         help="Modèle texte pour l'enrichissement ET l'arbitrage des désaccords")
    parser.add_argument("--base-url", type=str, default="https://llm.aristote.education/v1")
    parser.add_argument("--api-key", type=str, default="Dummy Key")
    parser.add_argument("--top-logprobs", type=int, default=5)

    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    image_files = list_images(input_dir)
    if not image_files:
        logger.error(f"Aucune image trouvée dans {input_dir}")
        return

    slug_a, slug_b = slugify(args.model_a), slugify(args.model_b)
    dir_a, dir_b = output_dir / slug_a, output_dir / slug_b
    dir_consensus = output_dir / "consensus"
    for d in (dir_a, dir_b, dir_consensus):
        d.mkdir(parents=True, exist_ok=True)

    analyzer_a = AristoteDocumentAnalyzer(
        base_url=args.base_url, api_key=args.api_key, top_logprobs=args.top_logprobs,
        **{_VISION_PARAM: args.model_a, _TEXT_PARAM: args.text_model},
    )
    analyzer_b = AristoteDocumentAnalyzer(
        base_url=args.base_url, api_key=args.api_key, top_logprobs=args.top_logprobs,
        **{_VISION_PARAM: args.model_b, _TEXT_PARAM: args.text_model},
    )
    arbitration_client = OpenAI(base_url=args.base_url, api_key=args.api_key)

    logger.info(f"{len(image_files)} images | A={args.model_a} | B={args.model_b} | arbitre/enrichissement={args.text_model}")

    start = time.time()
    for idx, image_file in enumerate(image_files, 1):
        logger.info(f"[{idx}/{len(image_files)}] {image_file.name}")
        try:
            process_single_image(
                image_file, analyzer_a, analyzer_b, args.model_a, args.model_b,
                args.text_model, arbitration_client, dir_a, dir_b, dir_consensus,
            )
        except Exception as e:
            logger.error(f"  Erreur inattendue sur {image_file.name}: {e}", exc_info=True)

    logger.info(f"\nTerminé en {round(time.time() - start, 1)}s.")
    logger.info(f"Résultats bruts : {dir_a} | {dir_b}")
    logger.info(f"Consensus fusionné : {dir_consensus}")


if __name__ == "__main__":
    main()