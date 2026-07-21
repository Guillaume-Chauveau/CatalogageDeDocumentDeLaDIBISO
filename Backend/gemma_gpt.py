#composite = worst_token_confidence × margin_factor × pénalité_structurelle

import json
import logging
import base64
import math
import time
import re
import argparse
from typing import Dict, Any, List, Optional
from pathlib import Path
from PIL import Image
import io

from openai import OpenAI

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# CONFIGURATION — adapt these to your setup
# 
API_BASE_URL = "https://llm.aristote.education/v1"
API_KEY       = "Dummy Key"           
MODEL_NAME    = "gemma-4-31b"   # <-- modèle VISION utilisé pour la passe 1 (extraction)
# Modèle TEXTE (sans image) utilisé pour la passe 2 (enrichissement : parsing des
# noms d'auteurs, domaine scientifique, romanisation optionnelle). À adapter au nom
# exact exposé par l'endpoint Aristote pour gpt-oss (ex: "gpt-oss-120b", "gpt-oss-20b"...).
ENRICHMENT_MODEL_NAME = "gpt-oss-120b"
TOP_LOGPROBS  = 5               # nombre d'alternatives par token à conserver



def encode_image_to_base64(image_path: str, max_pixels: int = 1024 * 1024) -> tuple[str, str]:
    """
    Opens an image, downscales it if it exceeds max_pixels, and returns
    (base64_string, mime_type) ready to embed in an OpenAI-compatible message.
    """
    image = Image.open(image_path).convert("RGB")

    # Downscale if needed (mirrors the original max_pixels cap)
    w, h = image.size
    if w * h > max_pixels:
        scale = (max_pixels / (w * h)) ** 0.5
        image = image.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        logger.debug(f"Image resized to {image.size} to stay within {max_pixels} pixels")

    suffix = Path(image_path).suffix.lower()
    mime_map = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                ".png": "image/png",  ".bmp": "image/bmp",
                ".tiff": "image/tiff", ".webp": "image/webp"}
    mime_type = mime_map.get(suffix, "image/jpeg")

    buffer = io.BytesIO()
    fmt = "JPEG" if mime_type == "image/jpeg" else suffix.lstrip(".").upper()
    image.save(buffer, format=fmt)
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return b64, mime_type


class AristoteDocumentAnalyzer:
    """
    Drop-in replacement for Qwen8BDocumentAnalyzer that calls a remote
    OpenAI-compatible vision endpoint instead of loading a local model.

    Cette version récupère en plus les log-probabilités token par token
    (paramètres `logprobs` / `top_logprobs` de l'API OpenAI-compatible)
    et calcule, par champ, un score de confiance composite basé sur :
      1. la confiance du PIRE token du champ (pas seulement la moyenne),
      2. la marge de logprob entre le token choisi et son meilleur
         concurrent (signal d'hésitation du modèle),
      3. une validation structurelle légère (regex de plausibilité).

    Le champ "publishers" est une LISTE d'objets {"publisher", "place"} ;
    il est scoré éditeur par éditeur (chaque sous-champ reçoit son propre
    score), puis agrégé au niveau du champ via le score le plus faible
    parmi tous les éditeurs (cohérent avec la logique "worst token").

    Le pipeline comporte deux passes :
      - Passe 1 (vision, modèle `model`) : extraction brute des métadonnées
        depuis l'image, y compris "translators" (traducteur(s) explicite(s),
        distincts des auteurs).
      - Passe 2 (texte seul, modèle `enrichment_model`, typiquement un
        modèle de raisonnement type gpt-oss) : ENRICHISSEMENT systématique
        — décomposition prénom/nom de chaque auteur ("authors_parsed") et
        identification du domaine scientifique ("scientific_field"). La
        romanisation reste une tâche OPTIONNELLE ajoutée au prompt/schéma
        de cette même passe uniquement si un script non-latin a été
        détecté en passe 1.
    """

    # Date plausible pour un document patrimonial (1400-2029)
    _DATE_RE = re.compile(r"^(1[4-9]\d{2}|20[0-2]\d)$")

    def __init__(self, base_url: str = API_BASE_URL, api_key: str = API_KEY,
                 model: str = MODEL_NAME, enrichment_model: str = ENRICHMENT_MODEL_NAME,
                 top_logprobs: int = TOP_LOGPROBS):
        self.model = model
        self.enrichment_model = enrichment_model
        self.top_logprobs = top_logprobs
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        logger.info(
            f"API client ready — vision model: {self.model} | "
            f"enrichment model: {self.enrichment_model} @ {base_url}"
        )


    # Public interface (identical signature to the original class)


    def process_image(self, image_path: str) -> dict:
        """Exécute le pipeline complet (passe 1 vision + passe 2 enrichissement) et formate la sortie en JSON."""
        start_time = time.time()
        logger.info(f"Analyse de {Path(image_path).name} (passe 1 : extraction vision)")

        ocr_prompt = (
            "Tu es un bibliothécaire expert spécialisé en catalogage (norme ISBD). "
            "Analyse l'image de couverture ou de page de titre et extrais les métadonnées "
            "pour correspondre EXACTEMENT à la structure JSON fournie.\n\n"
            "Règles strictes pour l'extraction :\n"
            "1. \"title\": Le titre principal de l'ouvrage uniquement (sans sous-titre).\n"
            "2. \"title_complement\": Le sous-titre ou complément du titre s'il existe "
            "(ce qui suit un ':' ou un '—' après le titre principal). Laisser vide sinon.\n"
            "3. \"volume_number\": Le numéro de volume ou de tome si l'ouvrage fait partie "
            "d'une suite ou d'une série (ex: 'Tome 2', 'Vol. III', 'Part 1'). "
            "Extraire uniquement le numéro/label tel qu'il apparaît. Laisser vide sinon.\n"
            "4. \"authors\": Le ou les auteurs, recopiés exactement tel qu'ils apparaissent sur "
            "l'image (ne pas reformater en 'Nom, Prénom' ni inverser l'ordre), SANS les titres, "
            "civilités ou qualificatifs (ex: 'M.', 'Mme', 'Dr.', 'Abbé', 'Professeur', 'Pr.', "
            "'Sir') qui précèdent ou suivent le nom : ne garder que le nom propre. Si plusieurs "
            "auteurs, les séparer par ' ; ', dans le même ordre que sur l'image.\n"
            "4bis. \"author_titles\": Les titres/civilités retirés des noms au point précédent, "
            "dans le MÊME ORDRE que les auteurs correspondants dans \"authors\", séparés par "
            "' ; '. Si un auteur donné n'a aucun titre, laisser une chaîne vide à sa position "
            "(ex: 'Dr. ;  ; Mme' si le 2e auteur sur 3 n'a pas de titre). Laisser entièrement "
            "vide (\"\") si aucun auteur n'a de titre visible.\n"
            "4ter. \"translators\": Le ou les TRADUCTEURS de l'ouvrage, uniquement s'ils sont "
            "explicitement mentionnés comme tels (ex: 'traduit par', 'traduit de l'allemand par', "
            "'translated by', 'trad.', 'übersetzt von'). Ne jamais confondre avec les auteurs : "
            "un nom ne va dans \"translators\" QUE si le texte indique explicitement une "
            "traduction. Recopier le(s) nom(s) exactement tel(s) qu'ils apparaissent, SANS les "
            "titres/civilités (même règle que pour \"authors\"). Si plusieurs traducteurs, "
            "séparer par ' ; ', dans l'ordre d'apparition. Laisser vide si aucun traducteur "
            "n'est mentionné.\n"
            "5. \"edition\": La mention d'édition telle qu'elle apparaît sur l'image "
            "(ex: '2e éd.', 'Nouvelle édition revue et augmentée', '3rd edition'). "
            "Laisser vide si aucune mention d'édition n'est visible.\n"
            "6. \"publishers\": Liste des éditeurs mentionnés. Pour chaque éditeur, indiquer "
            "son nom et la ville correspondante si elle est disponible. Si aucun éditeur "
            "commercial n'est identifiable, indiquer la collectivité responsable (institution, "
            "organisme, association, etc.) qui a publié l'ouvrage comme 'publisher'. "
            "Si plusieurs éditeurs se partagent la même ville, répéter la ville pour chacun. "
            "Si une ville n'est pas disponible pour un éditeur donné, laisser \"place\" vide "
            "pour cet éditeur. Format :\n"
            "   [{\"publisher\": \"\", \"place\": \"\"}, ...]\n"
            "7. \"collection\": Le nom de la collection ou série éditoriale à laquelle "
            "appartient l'ouvrage, si elle est mentionnée (ex: 'Bibliothèque des sciences "
            "physiques'). Laisser vide sinon.\n"
            "8. \"illustrations\": Si l'image mentionne la présence ou la nature d'illustrations "
            "(ex: 'avec 12 planches', 'illustré de figures dans le texte', 'ill.'), recopier "
            "ce texte tel qu'il apparaît, sans le reformuler ni le résumer. Laisser vide si "
            "aucune mention d'illustration n'est visible.\n"
            "9. \"date\": L'année de publication (4 chiffres).\n"
            "10. \"language\": La langue principale du document, déterminée en priorité à partir "
            "du titre (et des autres champs si le titre est ambigu ou trop court). Indiquer le nom "
            "de la langue en français (ex: 'français', 'allemand', 'suédois', 'russe', 'arabe', "
            "'chinois', 'grec'). Laisser vide si la langue est réellement indéterminable.\n"
            "11. \"script\": Le système graphique utilisé pour le titre. Répondre exactement "
            "'latin' si le texte est écrit avec l'alphabet latin (accents/diacritiques compris, "
            "ex: français, allemand, suédois, polonais), ou 'non_latin' s'il est écrit avec un "
            "autre système graphique (ex: cyrillique, grec, arabe, hébreu, chinois, japonais).\n"
            "Si une information est totalement absente de l'image, utilise une chaîne vide \"\" "
            "(ou une liste vide [] pour \"publishers\"). "
            "N'invente AUCUNE information absente du texte visible. Ne complète jamais un champ "
            "par déduction ou supposition : seule l'information explicitement lisible sur "
            "l'image doit être extraite.\n\n"
            "Format JSON requis (répondre UNIQUEMENT avec ce JSON, sans markdown, sans texte autour) :\n"
            "{\n"
            "  \"title\": \"\",\n"
            "  \"title_complement\": \"\",\n"
            "  \"volume_number\": \"\",\n"
            "  \"authors\": \"\",\n"
            "  \"author_titles\": \"\",\n"
            "  \"translators\": \"\",\n"
            "  \"edition\": \"\",\n"
            "  \"publishers\": [{\"publisher\": \"\", \"place\": \"\"}],\n"
            "  \"collection\": \"\",\n"
            "  \"illustrations\": \"\",\n"
            "  \"date\": \"\",\n"
            "  \"language\": \"\",\n"
            "  \"script\": \"\"\n"
            "}"
        )

        required_keys = {
            "title": "",
            "title_complement": "",
            "volume_number": "",
            "authors": "",
            "author_titles": "",
            "translators": "",
            "edition": "",
            "publishers": [],
            "collection": "",
            "illustrations": "",
            "date": "",
            "language": "",
            "script": "",
            # Champs produits par la passe 2 (enrichissement) :
            "scientific_field": "",
            "authors_parsed": [],
            "romanization": {
                "title": "",
                "title_complement": "",
                "volume_number": "",
                "authors": "",
                "translators": "",
                "edition": "",
                "publishers": [],
                "collection": "",
                "illustrations": "",
            },
        }

        # Clés de la passe 1 uniquement (tout sauf ce que produit la passe 2).
        pass1_keys = {
            k: v for k, v in required_keys.items()
            if k not in ("romanization", "authors_parsed", "scientific_field")
        }

        raw_response: str = ""
        token_logprobs: Optional[List[Dict[str, Any]]] = None
        logprobs_error: Optional[str] = None

        try:
            raw_response, token_logprobs, logprobs_error = self._generate(
                image_path=image_path, prompt=ocr_prompt, max_tokens=1500
            )
            logger.debug(f"Réponse brute du modèle (passe 1): {raw_response}")

            metadata = self._parse_json_tolerant(raw_response)
            if metadata is None:
                logger.warning("Impossible d'extraire les métadonnées, structure par défaut utilisée.")
                metadata = {}

            final_metadata = {**required_keys, **metadata}
            # "romanization" / "authors_parsed" / "scientific_field" sont produits
            # par la passe 2 : on les réinitialise à leur valeur par défaut ici,
            # même si le parsing tolérant de la passe 1 en aurait extrait des traces.
            final_metadata["romanization"] = required_keys["romanization"]
            final_metadata["authors_parsed"] = required_keys["authors_parsed"]
            final_metadata["scientific_field"] = required_keys["scientific_field"]

        except Exception as e:
            logger.error(f"Erreur lors du traitement de l'image (passe 1): {e}", exc_info=True)
            final_metadata = {**required_keys, "error": str(e)}

        process_time = time.time() - start_time

        result = {
            "image_filename": Path(image_path).name,
            "processing_time_seconds": round(process_time, 2),
            "metadata": final_metadata,
        }

        confidence_scores: Dict[str, Any] = {}

        if token_logprobs is not None:
            result["token_logprobs"] = token_logprobs
            # Score de confiance PAR CHAMP (aligné sur la valeur extraite, pas sur tout le JSON)
            confidence_scores = self._compute_field_confidences(
                raw_response=raw_response,
                token_logprobs=token_logprobs,
                required_keys=pass1_keys,
            )
        if logprobs_error:
            result["logprobs_error"] = logprobs_error

        # --- Passe 2 : enrichissement (modèle texte, ex: gpt-oss) ---
        # Toujours tentée dès qu'il y a un minimum de contenu exploitable en sortie
        # de la passe 1 (titre ou auteurs). Produit systématiquement :
        #   - "authors_parsed" : décomposition prénom / nom de famille par auteur
        #   - "scientific_field" : discipline scientifique du document
        # La romanisation reste OPTIONNELLE : elle n'est ajoutée au prompt/schéma
        # de cette passe que si un script non-latin a été détecté en passe 1.
        script_value = str(final_metadata.get("script") or "").strip().lower()
        is_non_latin = "non" in script_value and "latin" in script_value

        rom_scalar_keys = [
            "title", "title_complement", "volume_number", "authors", "translators",
            "edition", "collection", "illustrations",
        ]

        has_exploitable_content = bool(final_metadata.get("title")) or bool(final_metadata.get("authors"))

        if has_exploitable_content and "error" not in final_metadata:
            logger.info(
                "Lancement de la passe d'enrichissement (modèle: %s)%s.",
                self.enrichment_model,
                " avec romanisation" if is_non_latin else "",
            )
            try:
                fields_for_enrichment = {
                    "title": final_metadata.get("title", ""),
                    "title_complement": final_metadata.get("title_complement", ""),
                    "volume_number": final_metadata.get("volume_number", ""),
                    "authors": final_metadata.get("authors", ""),
                    "translators": final_metadata.get("translators", ""),
                    "edition": final_metadata.get("edition", ""),
                    "publishers": final_metadata.get("publishers", []),
                    "collection": final_metadata.get("collection", ""),
                    "illustrations": final_metadata.get("illustrations", ""),
                    "language": final_metadata.get("language", ""),
                    "script": final_metadata.get("script", ""),
                }
                enrich_raw, enrich_token_logprobs, enrich_logprobs_error = self._generate_enrichment(
                    fields=fields_for_enrichment,
                    include_romanization=is_non_latin,
                )
                logger.debug(f"Réponse brute du modèle (passe 2 - enrichissement): {enrich_raw}")

                enrich_metadata = self._parse_enrichment_response(enrich_raw, include_romanization=is_non_latin)
                if enrich_metadata is None:
                    logger.warning("Impossible d'extraire l'enrichissement, valeurs par défaut utilisées.")
                    enrich_metadata = {}

                final_metadata["scientific_field"] = enrich_metadata.get("scientific_field", "")
                final_metadata["authors_parsed"] = enrich_metadata.get("authors_parsed", [])
                if is_non_latin:
                    final_metadata["romanization"] = {
                        **required_keys["romanization"],
                        **enrich_metadata.get("romanization", {}),
                    }

                if enrich_token_logprobs is not None:
                    result["enrichment_token_logprobs"] = enrich_token_logprobs
                    enrich_spans, enrich_reference_text = self._build_spans_and_reference(
                        enrich_token_logprobs, enrich_raw
                    )
                    enrich_confidences = self._score_object_scalar_fields(
                        enrich_reference_text, enrich_spans, ["scientific_field"], scope_offset=0,
                    )
                    enrich_confidences["authors_parsed"] = self._score_list_field(
                        enrich_reference_text, enrich_spans, "authors_parsed",
                        ["raw", "given_name", "family_name"], scope_offset=0,
                    )
                    if is_non_latin:
                        rom_confidences = self._score_object_scalar_fields(
                            enrich_reference_text, enrich_spans, rom_scalar_keys, scope_offset=0,
                        )
                        rom_confidences["publishers"] = self._score_publishers_field(
                            enrich_reference_text, enrich_spans, scope_offset=0
                        )
                        enrich_confidences["romanization"] = rom_confidences
                    confidence_scores["enrichment"] = enrich_confidences
                if enrich_logprobs_error:
                    result["enrichment_logprobs_error"] = enrich_logprobs_error

            except Exception as e:
                logger.error(f"Erreur lors de la passe d'enrichissement: {e}", exc_info=True)
                result["enrichment_error"] = str(e)
        else:
            logger.info("Passe d'enrichissement ignorée (pas de titre/auteur exploitable en passe 1).")

        if confidence_scores:
            result["confidence_scores"] = confidence_scores

        return result


    # Private helpers — generation


    def _generate(
        self, image_path: str, prompt: str, max_tokens: int = 1500
    ) -> tuple[str, Optional[List[Dict[str, Any]]], Optional[str]]:
        """
        Sends image + prompt to the remote API and returns:
        (raw_text, token_logprobs, logprobs_error)
        """
        b64_image, mime_type = encode_image_to_base64(image_path)

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{b64_image}",
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ]

        return self._call_api(messages, max_tokens=max_tokens)

    def _generate_enrichment(
        self, fields: Dict[str, Any], include_romanization: bool, max_tokens: int = 4500,
    ) -> tuple[str, Optional[List[Dict[str, Any]]], Optional[str]]:
        """
        Passe 2, TEXTE SEUL (pas d'image), exécutée sur `self.enrichment_model`
        (modèle de raisonnement texte, ex: gpt-oss) plutôt que sur le modèle
        vision de la passe 1. Deux tâches systématiques :

          1. "authors_parsed" : décompose chaque auteur listé dans "authors"
             (chaîne séparée par ' ; ', même ordre) en prénom ("given_name")
             et nom de famille ("family_name"), en conservant le nom complet
             original dans "raw".
          2. "scientific_field" : identifie la discipline scientifique
             principale du document à partir du titre, de son complément et
             de la collection.

        La ROMANISATION reste optionnelle : elle n'est ajoutée au prompt et
        au schéma JSON attendu que si `include_romanization` est vrai
        (script non-latin détecté en passe 1). Séparer ces tâches de la
        passe 1 permet de garder les logprobs propres à chaque tâche (la
        confiance du parsing de noms ne doit pas être mélangée à celle de
        la lecture visuelle).
        """
        instructions = (
            "Tu es un bibliothécaire expert en catalogage patrimonial (norme ISBD) et en onomastique. "
            "À partir des métadonnées fournies ci-dessous, réalise les tâches de structuration suivantes. "
            "Tu dois impérativement respecter le format JSON de sortie demandé, sans aucun texte d'introduction ni de conclusion.\n\n"
            
            "### TÂCHES À RÉALISER :\n\n"
            
            "1. **Extraction des auteurs (`authors_parsed`)** :\n"
            "   Pour CHAQUE auteur présent dans le champ \"authors\" (les auteurs y sont séparés par des point-virgules ' ; ' dans leur ordre d'apparition) :\n"
            "   - `raw` : Conserve la chaîne de caractères originale de l'auteur.\n"
            "   - `family_name` : Extrais le nom de famille de l'auteur.\n"
            "   - `given_name` : Extrais le prénom. Si seules une ou plusieurs initiales sont présentes, inscris-les ici. "
            "Si le prénom est totalement absent, laisse ce champ vide (chaîne vide \"\").\n"
            "   *Règles d'or* : Utilise les conventions bibliographiques de la langue du document pour résoudre les cas d'ordre ambigu (ex: Nom Prénom vs Prénom Nom). "
            "N'invente JAMAIS un prénom absent du texte source. S'il n'y a aucun auteur, renvoie une liste vide [].\n\n"
            
            "2. **Discipline scientifique (`scientific_field`)** :\n"
            "   Identifie la discipline scientifique principale de l'ouvrage à partir du titre, de son complément et de la collection.\n"
            "   *Valeurs autorisées* : Choisis parmi 'chimie', 'physique', 'mathématiques', 'astronomie', 'botanique', 'zoologie', 'médecine', "
            "'histoire naturelle', 'géologie', 'minéralogie', 'sciences naturelles', 'ingénierie'.\n"
            "   *Règles d'or* : Réponds en français et en minuscules. Si la discipline ne peut pas être déterminée avec certitude, réponds exactement 'indéterminé'.\n\n"
            
            "### FORMAT DE SORTIE ATTENDU (JSON strict) :\n"
            "```json\n"
            "{\n"
            "  \"authors_parsed\": [\n"
            "    {\n"
            "      \"raw\": \"Nom d'origine\",\n"
            "      \"family_name\": \"Nom\",\n"
            "      \"given_name\": \"Prénom ou Initiale(s)\"\n"
            "    }\n"
            "  ],\n"
            "  \"scientific_field\": \"discipline_identifiée\"\n"
            "}\n"
            "```"
        )

        base_schema_fields = (
            "  \"scientific_field\": \"\",\n"
            "  \"authors_parsed\": [{\"raw\": \"\", \"given_name\": \"\", \"family_name\": \"\"}]"
        )

        if include_romanization:
            instructions += (
                "3. \"romanization\": fournis en plus une ROMANISATION (translittération "
                "standard en alphabet latin, PAS une traduction du sens) de chaque champ non "
                f"vide ci-dessous. Le document est en {fields.get('language') or 'langue inconnue'} "
                f"(système graphique : {fields.get('script') or 'non précisé'}). Utilise un "
                "système de translittération standard et largement reconnu pour cette langue "
                "(ex: ISO 9 pour le cyrillique, pinyin pour le chinois, romaji Hepburn pour le "
                "japonais, DIN 31635 ou ALA-LC pour l'arabe). Laisse vide tout champ déjà vide "
                "dans les données fournies. N'invente aucune information, ne traduis pas le "
                "sens des mots. La structure \"publishers\" reste une liste d'objets "
                "{\"publisher\", \"place\"}.\n"
            )
            schema = (
                "{\n"
                + base_schema_fields + ",\n"
                "  \"romanization\": {\n"
                "    \"title\": \"\",\n"
                "    \"title_complement\": \"\",\n"
                "    \"volume_number\": \"\",\n"
                "    \"authors\": \"\",\n"
                "    \"translators\": \"\",\n"
                "    \"edition\": \"\",\n"
                "    \"publishers\": [{\"publisher\": \"\", \"place\": \"\"}],\n"
                "    \"collection\": \"\",\n"
                "    \"illustrations\": \"\"\n"
                "  }\n"
                "}"
            )
        else:
            schema = "{\n" + base_schema_fields + "\n}"

        prompt = (
            instructions
            + f"\nDonnées disponibles :\n{json.dumps(fields, ensure_ascii=False)}\n\n"
            + "Réponds UNIQUEMENT avec ce JSON (sans markdown, sans texte autour) :\n"
            + schema
        )

        messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]

        return self._call_api(messages, max_tokens=max_tokens, model=self.enrichment_model)

    def _call_api(
        self, messages: List[Dict[str, Any]], max_tokens: int, model: Optional[str] = None,
    ) -> tuple[str, Optional[List[Dict[str, Any]]], Optional[str]]:
        """
        Appel API partagé par _generate (vision, passe 1) et
        _generate_enrichment (texte seul, passe 2). `model` permet de
        surcharger `self.model` (utilisé par défaut) — la passe 2 passe ici
        `self.enrichment_model` pour router vers un modèle texte distinct
        (ex: gpt-oss) plutôt que le modèle vision.

        Retourne (raw_text, token_logprobs, logprobs_error).
        token_logprobs est une liste de dicts:
            {
              "token": str,
              "logprob": float,
              "top_logprobs": [{"token": str, "logprob": float}, ...]
            }
        logprobs_error est renseigné si le endpoint refuse logprobs=True
        (certains serveurs ne le supportent pas), auquel cas on retente
        sans logprobs pour ne pas bloquer le pipeline.
        """
        model_name = model or self.model

        try:
            response = self.client.chat.completions.create(
                model=model_name,
                max_tokens=max_tokens,
                logprobs=True,
                top_logprobs=self.top_logprobs,
                messages=messages,
            )
        except Exception as e:
            # Fallback : le endpoint ne supporte pas logprobs pour ce modèle/route
            logger.warning(f"logprobs non supportés par l'API ({e}), nouvelle tentative sans logprobs.")
            response = self.client.chat.completions.create(
                model=model_name,
                max_tokens=max_tokens,
                messages=messages,
            )
            message = response.choices[0].message
            finish_reason = getattr(response.choices[0], "finish_reason", None)
            content = message.content

            if content is None:
                # Cas typique des modèles de raisonnement (ex: gpt-oss) : le contenu
                # final peut être vide si le modèle a épuisé max_tokens pendant sa
                # phase de raisonnement (finish_reason == "length"), ou si le
                # contenu se trouve dans un champ séparé (ex: reasoning_content)
                # selon l'implémentation du endpoint.
                reasoning_content = getattr(message, "reasoning_content", None)
                logger.warning(
                    f"content est None pour le modèle {model_name} "
                    f"(finish_reason={finish_reason!r}"
                    f"{', reasoning_content présent' if reasoning_content else ''}). "
                    "Réponse traitée comme vide."
                )
                content = ""

            text = content.strip()
            return text, None, f"logprobs indisponibles sur ce endpoint/modèle: {e}"

        message = response.choices[0].message
        finish_reason = getattr(response.choices[0], "finish_reason", None)
        content = message.content

        if content is None:
            # Cas typique des modèles de raisonnement (ex: gpt-oss) : le contenu
            # final peut être vide si le modèle a épuisé max_tokens pendant sa
            # phase de raisonnement (finish_reason == "length"), ou si le
            # contenu se trouve dans un champ séparé (ex: reasoning_content)
            # selon l'implémentation du endpoint.
            reasoning_content = getattr(message, "reasoning_content", None)
            logger.warning(
                f"content est None pour le modèle {model_name} "
                f"(finish_reason={finish_reason!r}"
                f"{', reasoning_content présent' if reasoning_content else ''}). "
                "Réponse traitée comme vide."
            )
            content = ""

        text = content.strip()

        token_logprobs: Optional[List[Dict[str, Any]]] = None
        choice_logprobs = getattr(response.choices[0], "logprobs", None)

        if choice_logprobs is not None and getattr(choice_logprobs, "content", None):
            token_logprobs = []
            for entry in choice_logprobs.content:
                top_list = []
                for top in (entry.top_logprobs or []):
                    top_list.append({
                        "token": top.token,
                        "logprob": top.logprob,
                    })
                token_logprobs.append({
                    "token": entry.token,
                    "logprob": entry.logprob,
                    "top_logprobs": top_list,
                })
        else:
            logger.warning("Le champ logprobs est vide dans la réponse (modèle/serveur non compatible).")

        return text, token_logprobs, None


    # Private helpers — confidence scoring


    def _token_margin(self, entry: Dict[str, Any]) -> Optional[float]:
        """
        Écart de logprob entre le token choisi et son meilleur concurrent
        parmi les top_logprobs renvoyés par l'API.

        Un écart important (ex: -0.1 vs -3.0) signifie que le modèle
        n'hésitait pas. Un écart proche de 0 (ex: -0.3 vs -0.35) signifie
        une hésitation réelle entre deux lectures possibles (ex: 'Dupont'
        vs 'Dupond', ou '1902' vs '1962'), même si le logprob absolu du
        token choisi semble correct.

        Renvoie None si top_logprobs est vide ou ne contient qu'une seule
        alternative identique au token choisi.
        """
        top = entry.get("top_logprobs") or []
        if not top:
            return None
        chosen_token = entry["token"]
        chosen_lp = entry["logprob"]
        runner_up_lp = next((t["logprob"] for t in top if t["token"] != chosen_token), None)
        if runner_up_lp is None:
            if len(top) >= 2:
                # Toutes les alternatives listées == le token choisi : on prend
                # la plus faible comme minorant conservateur de la marge.
                runner_up_lp = top[-1]["logprob"]
            else:
                return None
        return chosen_lp - runner_up_lp

    def _structural_validity(self, key: str, value: str) -> Optional[bool]:
        """
        Plausibilité STRUCTURELLE de la valeur extraite, indépendante de la
        confiance du modèle. Sert à détecter les cas où le modèle est
        confiant mais où la valeur est manifestement improbable (ex: une
        date hors plage plausible pour un fonds patrimonial).

        Renvoie None si aucune règle n'existe pour ce champ (pas de
        pénalité appliquée dans ce cas — absence de règle ≠ invalidité).
        """
        if not value:
            return None
        if key == "date":
            return bool(self._DATE_RE.match(value.strip()))
        if key == "authors":
            return bool(re.search(r"[A-ZÀ-Ÿ]", value))
        if key == "title":
            return len(value.strip()) >= 5
        return None

    def _empty_confidence(self, value: Optional[Any] = None) -> Dict[str, Any]:
        """Structure de retour par défaut quand un champ est vide ou non scorable."""
        return {
            "value": value,
            "confidence": None,
            "avg_token_confidence": None,
            "worst_token_confidence": None,
            "avg_logprob": None,
            "min_logprob": None,
            "avg_margin": None,
            "min_margin": None,
            "structurally_valid": None,
            "n_tokens": 0,
        }

    def _find_balanced_array_span(self, text: str, key: str) -> Optional[tuple[int, int]]:
        """
        Localise dans `text` le span [start, end) du tableau JSON associé à
        "key": [...], en comptant les crochets pour gérer les objets
        imbriqués (une regex non-greedy classique casserait dès qu'il y a
        un ']' dans une valeur, ou fusionnerait plusieurs tableaux avec un
        ']' trop loin).
        """
        return self._find_balanced_span(text, key, "[", "]")

    def _find_balanced_object_span(self, text: str, key: str) -> Optional[tuple[int, int]]:
        """Comme _find_balanced_array_span mais pour un objet "key": {...} (ex: romanization)."""
        return self._find_balanced_span(text, key, "{", "}")

    def _find_balanced_span(
        self, text: str, key: str, open_char: str, close_char: str
    ) -> Optional[tuple[int, int]]:
        """
        Localise dans `text` le span [start, end) de la valeur associée à
        "key": <open_char>...<close_char>, en comptant les délimiteurs pour
        gérer les objets/tableaux imbriqués (une regex non-greedy classique
        casserait dès qu'il y a un délimiteur de fermeture dans une valeur).
        """
        m = re.search(r'"' + re.escape(key) + r'"\s*:\s*' + re.escape(open_char), text)
        if not m:
            return None
        start = m.end() - 1  # position du délimiteur d'ouverture
        depth = 0
        for i in range(start, len(text)):
            if text[i] == open_char:
                depth += 1
            elif text[i] == close_char:
                depth -= 1
                if depth == 0:
                    return start, i + 1
        return None  # valeur non fermée (réponse tronquée)

    def _score_span(
        self, spans: List[Dict[str, Any]], val_start: int, val_end: int
    ) -> Optional[Dict[str, Any]]:
        """
        Agrège les logprobs des tokens dont >= 50% du span recouvre
        [val_start, val_end) et calcule les métriques de confiance brutes
        (sans pénalité structurelle, appliquée par l'appelant selon le
        champ). Renvoie None si aucun token ne recouvre suffisamment ce
        span (ex: valeur reconstruite hors synchro avec les offsets).
        """
        overlapping = []
        for s in spans:
            overlap = min(s["end"], val_end) - max(s["start"], val_start)
            tok_len = s["end"] - s["start"]
            if tok_len > 0 and overlap / tok_len >= 0.5:
                overlapping.append(s)

        if not overlapping:
            return None

        logprobs = [s["logprob"] for s in overlapping]
        margins = [s["margin"] for s in overlapping if s["margin"] is not None]

        avg_logprob = sum(logprobs) / len(logprobs)
        min_logprob = min(logprobs)
        avg_margin = sum(margins) / len(margins) if margins else None
        min_margin = min(margins) if margins else None

        avg_token_confidence = math.exp(avg_logprob)
        worst_token_confidence = math.exp(min_logprob)

        composite = worst_token_confidence
        if min_margin is not None:
            composite *= 1 / (1 + math.exp(-min_margin))  # sigmoïde dans (0,1)

        return {
            "raw_composite": composite,
            "avg_token_confidence": avg_token_confidence,
            "worst_token_confidence": worst_token_confidence,
            "avg_logprob": avg_logprob,
            "min_logprob": min_logprob,
            "avg_margin": avg_margin,
            "min_margin": min_margin,
            "n_tokens": len(overlapping),
        }

    def _build_scalar_confidence(
        self, key: str, value: str, val_start: int, val_end: int, spans: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Construit la structure de confiance finale pour un champ texte simple."""
        metrics = self._score_span(spans, val_start, val_end)
        if metrics is None:
            return self._empty_confidence(value)

        structurally_valid = self._structural_validity(key, value)
        composite = metrics["raw_composite"]
        if structurally_valid is False:
            composite *= 0.3

        return {
            "value": value,
            "confidence": round(composite, 4),
            "avg_token_confidence": round(metrics["avg_token_confidence"], 4),
            "worst_token_confidence": round(metrics["worst_token_confidence"], 4),
            "avg_logprob": round(metrics["avg_logprob"], 4),
            "min_logprob": round(metrics["min_logprob"], 4),
            "avg_margin": round(metrics["avg_margin"], 4) if metrics["avg_margin"] is not None else None,
            "min_margin": round(metrics["min_margin"], 4) if metrics["min_margin"] is not None else None,
            "structurally_valid": structurally_valid,
            "n_tokens": metrics["n_tokens"],
        }

    def _score_list_field(
        self,
        scope_text: str,
        spans: List[Dict[str, Any]],
        key: str,
        subkeys: List[str],
        scope_offset: int = 0,
    ) -> Dict[str, Any]:
        """
        Version générique du scoring "liste d'objets JSON" : score un champ
        comme "publishers" ({"publisher","place"}) ou "authors_parsed"
        ({"raw","given_name","family_name"}) sous-champ par sous-champ.

        `scope_text` est le texte dans lequel chercher la clé `key` (le
        document/réponse entière, ou un sous-texte imbriqué) ; `scope_offset`
        est la position de `scope_text` dans le texte de référence complet,
        pour convertir les positions locales en positions globales
        compatibles avec `spans` (toujours des offsets absolus).

        Chaque objet reçoit son propre score par sous-champ. Le score du
        champ dans son ensemble est le minimum des scores individuels
        (cohérent avec la logique "worst token" appliquée aux autres champs).

        Si le nombre de correspondances regex des sous-champs ne correspond
        pas au nombre attendu d'après json.loads (réponse mal formée /
        valeurs contenant des guillemets échappés complexes), on retombe
        sur un score agrégé unique pour tout le tableau plutôt que de
        risquer un appariement incorrect.
        """
        span = self._find_balanced_array_span(scope_text, key)
        if span is None:
            return self._empty_confidence([])

        local_arr_start, local_arr_end = span
        arr_start, arr_end = local_arr_start + scope_offset, local_arr_end + scope_offset
        array_text = scope_text[local_arr_start:local_arr_end]

        try:
            parsed_list = json.loads(array_text)
        except json.JSONDecodeError:
            parsed_list = None

        if not parsed_list:
            fallback_value = parsed_list if parsed_list is not None else array_text
            return self._empty_confidence(fallback_value)

        subkey_alt = "|".join(re.escape(k) for k in subkeys)
        sub_pattern = re.compile(r'"(' + subkey_alt + r')"\s*:\s*"((?:[^"\\]|\\.)*)"')
        matches = list(sub_pattern.finditer(array_text))

        # Compte les clés PRÉSENTES dans chaque objet (peu importe si leur
        # valeur est vide) : la regex matche aussi les valeurs vides, donc
        # compter seulement les valeurs non vides créerait une désynchro
        # artificielle et ferait basculer inutilement vers le fallback agrégé.
        expected_n_matches = sum(1 for obj in parsed_list for k in subkeys if k in obj)

        if len(matches) != expected_n_matches:
            # Désynchro regex/JSON : repli sur un score agrégé pour tout le tableau.
            metrics = self._score_span(spans, arr_start, arr_end)
            if metrics is None:
                return self._empty_confidence(parsed_list)
            return {
                "value": parsed_list,
                "confidence": round(metrics["raw_composite"], 4),
                "avg_token_confidence": round(metrics["avg_token_confidence"], 4),
                "worst_token_confidence": round(metrics["worst_token_confidence"], 4),
                "avg_logprob": round(metrics["avg_logprob"], 4),
                "min_logprob": round(metrics["min_logprob"], 4),
                "avg_margin": round(metrics["avg_margin"], 4) if metrics["avg_margin"] is not None else None,
                "min_margin": round(metrics["min_margin"], 4) if metrics["min_margin"] is not None else None,
                "structurally_valid": None,
                "n_tokens": metrics["n_tokens"],
                "note": f"score agrégé sur tout le tableau '{key}' (désynchro regex/JSON, scoring détaillé impossible)",
            }

        # Appariement séquentiel : on consomme les matches dans l'ordre pour
        # chaque objet parsé, dans l'ordre de ses clés présentes.
        match_iter = iter(matches)
        entries = []
        all_composites = []

        for obj in parsed_list:
            entry: Dict[str, Any] = {}
            for subkey in subkeys:
                if subkey not in obj:
                    entry[subkey] = self._empty_confidence("")
                    continue
                value = obj.get(subkey, "")
                # On consomme le match dans tous les cas (même valeur vide)
                # pour garder l'itérateur aligné avec les objets suivants.
                m = next(match_iter)
                if not value:
                    entry[subkey] = self._empty_confidence(value)
                    continue
                val_start = arr_start + m.start(2)
                val_end = arr_start + m.end(2)
                sub_conf = self._build_scalar_confidence(subkey, value, val_start, val_end, spans)
                entry[subkey] = sub_conf
                if sub_conf["confidence"] is not None:
                    all_composites.append(sub_conf["confidence"])
            entries.append(entry)

        field_confidence = min(all_composites) if all_composites else None

        return {
            "value": parsed_list,
            "confidence": field_confidence,
            f"{key}_detail": entries,
            f"n_{key}": len(entries),
        }

    def _score_publishers_field(
        self,
        scope_text: str,
        spans: List[Dict[str, Any]],
        scope_offset: int = 0,
    ) -> Dict[str, Any]:
        """Scoring du champ "publishers", éditeur par éditeur (cf. _score_list_field)."""
        return self._score_list_field(scope_text, spans, "publishers", ["publisher", "place"], scope_offset)

    def _score_object_scalar_fields(
        self,
        scope_text: str,
        spans: List[Dict[str, Any]],
        keys: List[str],
        scope_offset: int = 0,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Applique le scoring de champ texte simple (_build_scalar_confidence)
        à une liste de clés, à l'intérieur d'un `scope_text` donné (le
        document/réponse entier, ou le sous-texte d'un objet imbriqué comme
        "romanization"). `scope_offset` convertit les positions trouvées
        dans `scope_text` en positions absolues compatibles avec `spans`.
        """
        results: Dict[str, Dict[str, Any]] = {}
        for key in keys:
            pattern = re.compile(r'"' + re.escape(key) + r'"\s*:\s*"((?:[^"\\]|\\.)*)"')
            match = pattern.search(scope_text)

            if not match or match.group(1) == "":
                results[key] = self._empty_confidence(match.group(1) if match else None)
                continue

            value = match.group(1)
            local_start, local_end = match.span(1)
            val_start, val_end = local_start + scope_offset, local_end + scope_offset
            results[key] = self._build_scalar_confidence(key, value, val_start, val_end, spans)

        return results

    def _compute_field_confidences(
        self,
        raw_response: str,
        token_logprobs: List[Dict[str, Any]],
        required_keys: Dict[str, Any],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Calcule un score de confiance composite PAR CHAMP, en n'agrégeant
        que les logprobs des tokens qui recouvrent la VALEUR de ce champ
        dans le texte brut (pas les accolades/guillemets/clés JSON).

        Le champ "publishers" (liste d'objets) est traité séparément par
        _score_publishers_field, car il ne peut pas être capturé par la
        regex simple '"key": "valeur"' utilisée pour les champs texte.

        Le score composite combine trois signaux pour les champs texte :
          - worst_token_confidence : exp(min_logprob) du champ. Un seul
            token très incertain suffit à rendre tout le champ suspect ;
            la moyenne masquerait ce signal.
          - margin_factor : sigmoïde de la marge minimale top1/top2,
            traduit l'hésitation locale du modèle en un facteur (0,1).
          - pénalité structurelle : x0.3 si une règle de plausibilité
            échoue (pas x0, car la règle elle-même peut se tromper).

        Toutes les composantes brutes (avg/min logprob, avg/min margin,
        validité structurelle) sont conservées dans la sortie pour
        permettre une analyse de calibration a posteriori (utile pour
        comparer la fiabilité des scores entre modèles VLM).
        """
        if not token_logprobs:
            return {k: self._empty_confidence() for k in required_keys}

        spans, reference_text = self._build_spans_and_reference(token_logprobs, raw_response)

        confidences: Dict[str, Dict[str, Any]] = {}

        # Clés texte simples à scorer directement sur le document entier
        # (tout required_keys sauf "publishers", géré à part).
        scalar_keys = [k for k in required_keys if k != "publishers"]
        confidences.update(
            self._score_object_scalar_fields(reference_text, spans, scalar_keys, scope_offset=0)
        )

        if "publishers" in required_keys:
            confidences["publishers"] = self._score_publishers_field(reference_text, spans)

        return confidences

    def _build_spans_and_reference(
        self, token_logprobs: List[Dict[str, Any]], raw_response: str
    ) -> tuple[List[Dict[str, Any]], str]:
        """
        Reconstruit les offsets (start, end) de chaque token dans le texte
        concaténé, et renvoie (spans, reference_text) — reference_text est
        le texte reconstruit à partir des tokens, utilisé comme référence
        pour tous les calculs d'overlap afin de rester cohérent avec les
        offsets même en cas de légère désynchro d'encodage avec raw_response.
        Factorisé pour être réutilisé aussi bien pour la passe 1
        (extraction) que pour la passe 2 (enrichissement) — deux réponses
        API distinctes, chacune avec ses propres token_logprobs.
        """
        spans: List[Dict[str, Any]] = []
        pos = 0
        pieces = []
        for entry in token_logprobs:
            tok = entry["token"]
            start, end = pos, pos + len(tok)
            spans.append({
                "start": start,
                "end": end,
                "logprob": entry["logprob"],
                "margin": self._token_margin(entry),
            })
            pos = end
            pieces.append(tok)

        reconstructed = "".join(pieces)
        if reconstructed != raw_response:
            logger.warning(
                "Le texte reconstruit à partir des tokens ne correspond pas exactement "
                "à la réponse brute (probable désynchro d'encodage) — les scores de "
                "confiance par champ sont calculés sur le texte reconstruit par tokens, "
                "utilisé ici comme référence pour rester cohérent avec les offsets."
            )
            return spans, reconstructed
        return spans, raw_response


    # Private helpers — JSON parsing / repair


    def _repair_json_string(self, json_string: str) -> str | None:
        """Répare les JSON mal formatés ou incomplets."""
        json_string = json_string.replace("```json", "").replace("```", "").strip()
        if not json_string or json_string[0] not in "{[":
            return None
        last_brace_idx = max(json_string.rfind("}"), json_string.rfind("]"))
        if last_brace_idx != -1:
            json_string = json_string[: last_brace_idx + 1]
        return json_string

    def _parse_json_tolerant(self, response: str) -> Dict[str, Any] | None:
        """Parse du JSON de manière tolérante avec stratégies de repli."""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        repaired = self._repair_json_string(response)
        if repaired:
            try:
                return json.loads(repaired)
            except json.JSONDecodeError:
                pass

        logger.warning("Impossible de parser le JSON, tentative d'extraction regex avancée")
        extracted: Dict[str, Any] = {}

        # --- Champs texte simples ---
        for key in ("title", "title_complement", "volume_number", "edition", "collection",
                    "illustrations", "date", "author_titles", "translators"):
            m = re.search(r'"' + key + r'"\s*:\s*"([^"]*)"', response)
            extracted[key] = m.group(1) if m else ""

        # --- authors : gère aussi le cas où le modèle renvoie une liste ---
        authors_match = re.search(r'"authors"\s*:\s*"([^"]*)"', response)
        if authors_match:
            extracted["authors"] = authors_match.group(1).strip()
        else:
            authors_list_match = re.search(r'"authors"\s*:\s*(\[[^\]]*\])', response)
            if authors_list_match:
                try:
                    extracted["authors"] = json.loads(authors_list_match.group(1))
                except json.JSONDecodeError:
                    names = re.findall(r'"([^"\\]*(?:\\.[^"\\]*)*)"', authors_list_match.group(1))
                    extracted["authors"] = names if names else ""
            else:
                extracted["authors"] = ""

        # --- publishers : tableau d'objets, tentative de parsing tolérant du span brut ---
        extracted["publishers"] = self._extract_publishers_array(response)

        # --- language / script : champs texte simples ---
        for key in ("language", "script"):
            m = re.search(r'"' + key + r'"\s*:\s*"([^"]*)"', response)
            extracted[key] = m.group(1) if m else ""

        has_content = any(
            (v if not isinstance(v, (list, dict)) else len(v) > 0) for v in extracted.values()
        )
        return extracted if has_content else None

    def _parse_enrichment_response(self, response: str, include_romanization: bool) -> Dict[str, Any] | None:
        """
        Parse tolérant dédié à la réponse (plate, sans image) de la passe 2
        d'enrichissement : {scientific_field, authors_parsed, [romanization]}.
        Même stratégie de repli en cascade que _parse_json_tolerant (JSON
        strict -> réparation -> extraction regex champ par champ).
        """
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        repaired = self._repair_json_string(response)
        if repaired:
            try:
                return json.loads(repaired)
            except json.JSONDecodeError:
                pass

        logger.warning("Impossible de parser le JSON d'enrichissement, extraction regex de repli")

        extracted: Dict[str, Any] = {}

        m = re.search(r'"scientific_field"\s*:\s*"([^"]*)"', response)
        extracted["scientific_field"] = m.group(1) if m else ""

        authors_span = self._find_balanced_array_span(response, "authors_parsed")
        if authors_span:
            array_text = response[authors_span[0]:authors_span[1]]
            try:
                extracted["authors_parsed"] = json.loads(array_text)
            except json.JSONDecodeError:
                raws = re.findall(r'"raw"\s*:\s*"([^"]*)"', array_text)
                givens = re.findall(r'"given_name"\s*:\s*"([^"]*)"', array_text)
                familys = re.findall(r'"family_name"\s*:\s*"([^"]*)"', array_text)
                extracted["authors_parsed"] = [
                    {
                        "raw": r,
                        "given_name": givens[i] if i < len(givens) else "",
                        "family_name": familys[i] if i < len(familys) else "",
                    }
                    for i, r in enumerate(raws)
                ]
        else:
            extracted["authors_parsed"] = []

        if include_romanization:
            rom_span = self._find_balanced_object_span(response, "romanization")
            if rom_span:
                rom_text = response[rom_span[0]:rom_span[1]]
                try:
                    extracted["romanization"] = json.loads(rom_text)
                except json.JSONDecodeError:
                    extracted["romanization"] = {}
            else:
                extracted["romanization"] = {}

        has_content = bool(extracted.get("scientific_field")) or bool(extracted.get("authors_parsed"))
        return extracted if has_content else None

    def _extract_publishers_array(self, text: str) -> List[Dict[str, str]]:
        """
        Extraction tolérante d'un tableau "publishers": [...] depuis un
        texte (document entier ou sous-texte de romanization). Tente un
        parsing JSON strict du span équilibré, puis retombe sur une
        extraction régulière des paires publisher/place isolées.
        """
        span = self._find_balanced_array_span(text, "publishers")
        if not span:
            return []

        array_text = text[span[0]:span[1]]
        try:
            parsed = json.loads(array_text)
            return parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            pubs = re.findall(r'"publisher"\s*:\s*"([^"]*)"', array_text)
            places = re.findall(r'"place"\s*:\s*"([^"]*)"', array_text)
            if not pubs:
                return []
            return [
                {"publisher": p, "place": (places[i] if i < len(places) else "")}
                for i, p in enumerate(pubs)
            ]



# BATCH HELPER


def process_batch(analyzer: AristoteDocumentAnalyzer, input_dir: Path, output_dir: Path):
    """Processes a folder of images and saves results to JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)

    image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}
    image_files = sorted(
        [f for f in input_dir.iterdir() if f.suffix.lower() in image_extensions]
    )

    if not image_files:
        logger.warning(f"No images found in {input_dir}")
        return

    logger.info(f"Starting batch processing of {len(image_files)} images…")

    for idx, image_file in enumerate(image_files, 1):
        json_path = output_dir / f"{image_file.stem}.json"

        if json_path.exists():
            logger.info(f"[{idx}/{len(image_files)}] Ignoré (déjà traité) : {image_file.name}")
            continue

        logger.info(f"[{idx}/{len(image_files)}] Analyzing: {image_file.name}")
        try:
            result = analyzer.process_image(str(image_file))
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            logger.info(f"  -> Done in {result['processing_time_seconds']}s")
        except Exception as e:
            logger.error(f"  -> Error processing {image_file.name}: {e}")

    logger.info(f"\nBatch complete! All results saved to {output_dir}")



# CLI INTERFACE


def main():
    parser = argparse.ArgumentParser(
        description="Aristote API Vision OCR Pipeline (OpenAI-compatible) avec log-probas et passe d'enrichissement"
    )
    parser.add_argument("--image",  type=str, help="Process a single image path")
    parser.add_argument("--batch",  type=str, help="Process a directory of images")
    parser.add_argument("--output", type=str, default="./outputs/aristote_results",
                        help="Output directory")
    parser.add_argument("--base-url", type=str, default=API_BASE_URL,
                        help="API base URL")
    parser.add_argument("--api-key", type=str, default=API_KEY,
                        help="API key")
    parser.add_argument("--model",   type=str, default=MODEL_NAME,
                        help="Modèle VISION utilisé pour la passe 1 (extraction)")
    parser.add_argument("--enrichment-model", type=str, default=ENRICHMENT_MODEL_NAME,
                        help="Modèle TEXTE utilisé pour la passe 2 (enrichissement, ex: gpt-oss)")
    parser.add_argument("--top-logprobs", type=int, default=TOP_LOGPROBS,
                        help="Nombre d'alternatives de tokens à conserver par position")

    args = parser.parse_args()

    if not args.image and not args.batch:
        parser.print_help()
        return

    analyzer   = AristoteDocumentAnalyzer(base_url=args.base_url,
                                          api_key=args.api_key,
                                          model=args.model,
                                          enrichment_model=args.enrichment_model,
                                          top_logprobs=args.top_logprobs)
    output_dir = Path(args.output)

    if args.image:
        logger.info(f"Processing single image: {args.image}")
        result = analyzer.process_image(args.image)

        output_dir.mkdir(parents=True, exist_ok=True)
        json_path = output_dir / f"{Path(args.image).stem}_results.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"\nDONE in {result['processing_time_seconds']}s")
        print(f"Results saved to: {json_path}")

    elif args.batch:
        process_batch(analyzer, Path(args.batch), output_dir)


if __name__ == "__main__":
    main()
