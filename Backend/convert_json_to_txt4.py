"""
Convertit les JSON produits par gemma_gpt.py (process_image / process_batch)
en fichiers .txt au format plat :

    nom_du_champ$valeur$score_de_confiance$0

Une ligne par champ, dans un ordre et une nomenclature FIXES (31 champs),
adaptés à l'import cible :

    Article, Titre, Titre Romanisé, Complement du titre,
    Complement du titre Romanisé, Auteur, Auteur Romanisé,
    Numero du volume, Numero du volume Romanisé, Collection,
    Collection Romanisée, Ville, Ville Romanisée, Editeur,
    Editeur Romanisé, Mention d'edition, Mention d'edition Romanisée,
    Annee, Volume, Illustration, Illustration Romanisée, Dimension,
    Indexation Rameau, Premier Auteur, Co-Auteur, Role Auteur,
    Role CoAuteur, Auteur Secondaire, Role Auteur Secondaire,
    Nom de la Collectivite, Role de la Collectivite

Mapping retenu (validé avec l'utilisateur) :
  - Article, Dimension, Nom de la Collectivite, Role de la Collectivite :
    non produits par le VLM -> ligne vide ($$$0).
  - Volume (distinct de "Numero du volume" = volume_number) : non produit
    par le VLM -> ligne vide.
  - Indexation Rameau <- metadata["scientific_field"] (passe d'enrichissement).
  - Mention d'edition <- metadata["edition"].
  - Auteur <- metadata["authors"] (tous les auteurs, tel qu'extraits en passe 1).
  - Premier Auteur / Co-Auteur <- authors_parsed[0]/[1] ("raw"), produits
    en passe d'enrichissement.
  - Role Auteur / Role CoAuteur <- author_titles (1er / 2e titre de la
    liste ' ; '-séparée, dans le même ordre que les auteurs).
  - Auteur Secondaire <- concaténation de metadata["translators"],
    metadata["illustrators"] et metadata["prefaciers"] (tous extraits en
    passe 1, exactement comme "translators"), dans cet ordre.
  - Role Auteur Secondaire <- rôle littéral associé à chaque nom ci-dessus,
    dans le même ordre ("traducteur" / "illustrateur" / "préfacier"),
    aucune donnée de "rôle" n'étant extraite telle quelle par le VLM.
  - Champs "* Romanisé(e)" <- metadata["romanization"][...] (passe 2,
    déclenchée uniquement si le script détecté n'est pas latin). Reprennent
    exactement le même champ source que leur pendant non-romanisé (ex:
    "Titre Romanisé" <- romanization["title"]), mais avec leur propre score
    de confiance (conf_root["romanization"][...]["confidence"]). Vides
    ($$$0-like, confiance vide) si la passe de romanisation n'a pas été
    déclenchée pour ce document.

Usage :
    python json_to_txt.py --input resultat.json --output resultat.txt
    python json_to_txt.py --batch dossier_json/ --output dossier_txt/
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


# Ordre et libellés EXACTS des champs de sortie.
FIELD_ORDER = [
    "Article",
    "Titre",
    "Titre Romanisé",
    "Complement du titre",
    "Complement du titre Romanisé",
    "Auteur",
    "Auteur Romanisé",
    "Numero du volume",
    "Numero du volume Romanisé",
    "Collection",
    "Collection Romanisée",
    "Ville",
    "Ville Romanisée",
    "Editeur",
    "Editeur Romanisé",
    "Mention d'edition",
    "Mention d'edition Romanisée",
    "Annee",
    "Volume",
    "Illustration",
    "Illustration Romanisée",
    "Dimension",
    "Indexation Rameau",
    "Premier Auteur",
    "Co-Auteur",
    "Role Auteur",
    "Role CoAuteur",
    "Auteur Secondaire",
    "Role Auteur Secondaire",
    "Nom de la Collectivite",
    "Role de la Collectivite",
    "Langue",
]


# Utilitaires de formatage (repris de la version précédente)


def fmt_value(value: Any) -> str:
    """Nettoie une valeur scalaire pour l'écriture (pas de '$' ni retour ligne)."""
    if value is None:
        return ""
    s = str(value).strip()
    return s.replace("$", "").replace("\n", " ").replace("\r", " ")


def fmt_confidence(conf: Optional[float]) -> str:
    if conf is None:
        return ""
    return f"{conf:.4f}"


def join_multi(values: List[Any]) -> str:
    """Joint plusieurs valeurs avec '; ', en ignorant les vides."""
    cleaned = [fmt_value(v) for v in values if v and str(v).strip()]
    return "; ".join(cleaned)


def split_multi(value: str) -> List[str]:
    """Éclate une chaîne 'a ; b ; c' (séparateur ' ; ' ou ';') en liste."""
    if not value:
        return []
    return [p.strip() for p in value.split(";") if p.strip()]


def min_conf(confidences: List[Optional[float]]) -> Optional[float]:
    vals = [c for c in confidences if c is not None]
    return min(vals) if vals else None


def get_confidence(conf_root: Dict[str, Any], key: str) -> Optional[float]:
    entry = conf_root.get(key)
    if isinstance(entry, dict):
        return entry.get("confidence")
    return None


# Construction des lignes


def build_lines(result: Dict[str, Any]) -> List[str]:
    metadata = result.get("metadata", {}) or {}
    confidence_scores = result.get("confidence_scores", {}) or {}

    # "scientific_field", "authors_parsed" et "romanization" sont produits par
    # la passe d'enrichissement et stockés sous confidence_scores["enrichment"] ;
    # on les remonte au même niveau que le reste des scores pass1.
    enrichment_conf = confidence_scores.get("enrichment", {}) or {}
    conf_root = {
        **{k: v for k, v in confidence_scores.items() if k != "enrichment"},
        **enrichment_conf,
    }

    # "romanization" (passe 2, uniquement si script non-latin détecté) :
    # metadata["romanization"] contient les champs romanisés (title,
    # title_complement, volume_number, authors, edition, publishers,
    # collection, illustrations) ; conf_root["romanization"] contient le
    # score de confiance correspondant, par champ, exactement dans le même
    # format que les scores pass1 (ex: conf_root["romanization"]["title"]["confidence"]).
    metadata_rom = metadata.get("romanization", {}) or {}
    conf_root_rom = conf_root.get("romanization", {}) or {}
    if not isinstance(conf_root_rom, dict):
        conf_root_rom = {}

    lines: List[str] = []

    def add_empty(name: str) -> None:
        lines.append(f"{name}$$$0")

    def add_scalar(name: str, metadata_key: str, multi_value: bool = False,
                   metadata_src: Optional[Dict[str, Any]] = None,
                   conf_src: Optional[Dict[str, Any]] = None) -> None:
        metadata_src = metadata if metadata_src is None else metadata_src
        conf_src = conf_root if conf_src is None else conf_src
        raw = metadata_src.get(metadata_key, "")
        value_str = join_multi(split_multi(raw)) if multi_value else fmt_value(raw)
        conf = get_confidence(conf_src, metadata_key)
        lines.append(f"{name}${value_str}${fmt_confidence(conf)}$0")

    def add_scalar_rom(name: str, metadata_key: str, multi_value: bool = False) -> None:
        """Version romanisée d'add_scalar : lit dans metadata_rom / conf_root_rom."""
        add_scalar(name, metadata_key, multi_value=multi_value,
                   metadata_src=metadata_rom, conf_src=conf_root_rom)

    # --- Article : non généré ---
    add_empty("Article")

    # --- Titre / Complement du titre ---
    add_scalar("Titre", "title")
    add_scalar_rom("Titre Romanisé", "title")
    add_scalar("Complement du titre", "title_complement")
    add_scalar_rom("Complement du titre Romanisé", "title_complement")

    # --- Auteur (tous les auteurs, valeur brute passe 1) ---
    add_scalar("Auteur", "authors", multi_value=True)
    add_scalar_rom("Auteur Romanisé", "authors", multi_value=True)

    # --- Numero du volume / Collection ---
    add_scalar("Numero du volume", "volume_number")
    add_scalar_rom("Numero du volume Romanisé", "volume_number")
    add_scalar("Collection", "collection")
    add_scalar_rom("Collection Romanisée", "collection")

    add_scalar("Langue", "language")


    # --- Ville / Editeur (issus de publishers[], scorés éditeur par éditeur) ---
    def extract_publishers(pub_list: List[Any], conf_src: Dict[str, Any]):
        pub_conf_entry = conf_src.get("publishers", {}) if isinstance(conf_src.get("publishers", {}), dict) else {}
        pub_detail = pub_conf_entry.get("publishers_detail", []) or []

        villes = [p.get("place", "") for p in pub_list if isinstance(p, dict)]
        editeurs = [p.get("publisher", "") for p in pub_list if isinstance(p, dict)]

        if pub_detail:
            ville_conf = min_conf([d.get("place", {}).get("confidence") for d in pub_detail if isinstance(d, dict)])
            editeur_conf = min_conf([d.get("publisher", {}).get("confidence") for d in pub_detail if isinstance(d, dict)])
        else:
            ville_conf = pub_conf_entry.get("confidence")
            editeur_conf = pub_conf_entry.get("confidence")

        return villes, editeurs, ville_conf, editeur_conf

    publishers = metadata.get("publishers", []) or []
    villes, editeurs, ville_conf, editeur_conf = extract_publishers(publishers, conf_root)

    lines.append(f"Ville${join_multi(villes)}${fmt_confidence(ville_conf)}$0")

    # --- Ville / Editeur Romanisés (metadata["romanization"]["publishers"]) ---
    publishers_rom = metadata_rom.get("publishers", []) or []
    villes_rom, editeurs_rom, ville_rom_conf, editeur_rom_conf = extract_publishers(publishers_rom, conf_root_rom)

    lines.append(f"Ville Romanisée${join_multi(villes_rom)}${fmt_confidence(ville_rom_conf)}$0")
    lines.append(f"Editeur${join_multi(editeurs)}${fmt_confidence(editeur_conf)}$0")
    lines.append(f"Editeur Romanisé${join_multi(editeurs_rom)}${fmt_confidence(editeur_rom_conf)}$0")

    # --- Mention d'edition / Annee ---
    add_scalar("Mention d'edition", "edition")
    add_scalar_rom("Mention d'edition Romanisée", "edition")
    add_scalar("Annee", "date")

    # --- Volume : non généré (distinct de "Numero du volume") ---
    add_empty("Volume")

    # --- Illustration ---
    add_scalar("Illustration", "illustrations")
    add_scalar_rom("Illustration Romanisée", "illustrations")

    # --- Dimension : non généré ---
    add_empty("Dimension")

    # --- Indexation Rameau (= scientific_field, passe d'enrichissement) ---
    add_scalar("Indexation Rameau", "scientific_field")

    # --- Premier Auteur / Co-Auteur (authors_parsed[0]/[1], passe d'enrichissement) ---
    authors_parsed = metadata.get("authors_parsed", []) or []
    ap_conf_entry = conf_root.get("authors_parsed", {}) if isinstance(conf_root.get("authors_parsed", {}), dict) else {}
    ap_detail = ap_conf_entry.get("authors_parsed_detail", []) or []

    def author_raw(idx: int) -> str:
        if idx < len(authors_parsed) and isinstance(authors_parsed[idx], dict):
            return fmt_value(authors_parsed[idx].get("raw", ""))
        return ""

    def author_raw_conf(idx: int) -> Optional[float]:
        if idx < len(ap_detail) and isinstance(ap_detail[idx], dict):
            return ap_detail[idx].get("raw", {}).get("confidence")
        return None

    lines.append(f"Premier Auteur${author_raw(0)}${fmt_confidence(author_raw_conf(0))}$0")
    lines.append(f"Co-Auteur${author_raw(1)}${fmt_confidence(author_raw_conf(1))}$0")

    # --- Role Auteur / Role CoAuteur (author_titles, même ordre que les auteurs) ---
    titles = split_multi(metadata.get("author_titles", ""))
    titles_conf = get_confidence(conf_root, "author_titles")
    role_auteur = titles[0] if len(titles) > 0 else ""
    role_coauteur = titles[1] if len(titles) > 1 else ""

    lines.append(f"Role Auteur${fmt_value(role_auteur)}${fmt_confidence(titles_conf if role_auteur else None)}$0")
    lines.append(f"Role CoAuteur${fmt_value(role_coauteur)}${fmt_confidence(titles_conf if role_coauteur else None)}$0")

    # --- Auteur Secondaire (traducteurs, illustrateurs, préfaciers) / Role Auteur Secondaire ---
    # Chacun des trois champs est extrait en passe 1 exactement comme
    # "translators" (metadata["translators"] / ["illustrators"] / ["prefaciers"]),
    # aucune donnée de "rôle" n'étant produite telle quelle par le VLM : le rôle
    # est donc forcé littéralement selon le champ source, dans l'ordre de
    # concaténation ci-dessous (traducteurs, puis illustrateurs, puis préfaciers).
    secondary_sources = [
        ("translators", "traducteur"),
        ("illustrators", "illustrateur"),
        ("prefaciers", "préfacier"),
    ]

    secondary_names: List[str] = []
    secondary_roles: List[str] = []
    secondary_confs: List[Optional[float]] = []

    for metadata_key, role_label in secondary_sources:
        names = split_multi(metadata.get(metadata_key, ""))
        if not names:
            continue
        conf = get_confidence(conf_root, metadata_key)
        secondary_names.extend(names)
        secondary_roles.extend([role_label] * len(names))
        secondary_confs.extend([conf] * len(names))

    auteur_secondaire = join_multi(secondary_names)
    role_auteur_secondaire = join_multi(secondary_roles)
    secondaire_conf = min_conf(secondary_confs)

    lines.append(f"Auteur Secondaire${auteur_secondaire}${fmt_confidence(secondaire_conf)}$0")
    lines.append(
        f"Role Auteur Secondaire${role_auteur_secondaire}"
        f"${fmt_confidence(secondaire_conf if role_auteur_secondaire else None)}$0"
    )

    # --- Collectivité : non généré ---
    add_empty("Nom de la Collectivite")
    add_empty("Role de la Collectivite")

    return lines


def convert_file(json_path: Path, txt_path: Path) -> None:
    with open(json_path, "r", encoding="utf-8") as f:
        result = json.load(f)

    lines = build_lines(result)

    txt_path.parent.mkdir(parents=True, exist_ok=True)
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Convertit les JSON Biblinum en txt plat ($ séparateurs)")
    parser.add_argument("--input", type=str, help="Fichier JSON unique à convertir")
    parser.add_argument("--batch", type=str, help="Dossier de fichiers JSON à convertir")
    parser.add_argument("--output", type=str, required=True,
                        help="Fichier .txt de sortie (mode --input) ou dossier de sortie (mode --batch)")
    args = parser.parse_args()

    if not args.input and not args.batch:
        parser.print_help()
        return

    if args.input:
        convert_file(Path(args.input), Path(args.output))
        print(f"OK -> {args.output}")

    elif args.batch:
        input_dir = Path(args.batch)
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)

        json_files = sorted(input_dir.glob("*.json"))
        if not json_files:
            print(f"Aucun fichier .json trouvé dans {input_dir}")
            return

        for jf in json_files:
            txt_path = output_dir / f"{jf.stem}.txt"
            try:
                convert_file(jf, txt_path)
                print(f"OK  {jf.name} -> {txt_path.name}")
            except Exception as e:
                print(f"ERREUR sur {jf.name}: {e}")


if __name__ == "__main__":
    main()