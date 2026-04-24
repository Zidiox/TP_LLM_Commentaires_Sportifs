"""
services/analyzer.py
Service d'analyse LLM via l'API Groq (llama-3.3-70b).
Analyse le texte transcrit chunk par chunk et retourne des actions structurées en JSON.
"""

import json
import logging
import time

import requests

from backend.config import (
    GROQ_API_KEY,
    GROQ_CHAT_URL,
    LLM_MODEL,
    SYSTEM_PROMPT_TEMPLATE,
)
from backend.models import ActionDetail
from backend.utils.text_utils import split_text_into_chunks

logger = logging.getLogger(__name__)

# Délai entre chaque appel LLM pour respecter les rate limits de Groq (req/min)
RATE_LIMIT_DELAY: float = 1.5


def _empty_usage() -> dict[str, int]:
    return {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "requests": 0,
    }


def _merge_usage(total: dict[str, int], part: dict[str, int]) -> dict[str, int]:
    return {
        "prompt_tokens": total.get("prompt_tokens", 0) + part.get("prompt_tokens", 0),
        "completion_tokens": total.get("completion_tokens", 0) + part.get("completion_tokens", 0),
        "total_tokens": total.get("total_tokens", 0) + part.get("total_tokens", 0),
        "requests": total.get("requests", 0) + part.get("requests", 0),
    }


def _extract_usage(payload: dict) -> dict[str, int]:
    usage = payload.get("usage") or {}
    return {
        "prompt_tokens": int(usage.get("prompt_tokens", 0) or 0),
        "completion_tokens": int(usage.get("completion_tokens", 0) or 0),
        "total_tokens": int(usage.get("total_tokens", 0) or 0),
        "requests": 1,
    }


def _call_llm(chunk: str, system_prompt: str) -> tuple[list[ActionDetail], dict[str, int]]:
    """
    Appelle le LLM Groq sur un chunk de texte et retourne les actions détectées.

    Args:
        chunk: Extrait de texte transcrit à analyser.
        system_prompt: Prompt système formaté avec les noms des combattants.

    Returns:
        Liste d'ActionDetail parsés depuis la réponse JSON du LLM.
        Retourne une liste vide si la réponse ne peut pas être parsée.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}",
    }
    payload = {
        "model": LLM_MODEL,
        "temperature": 0.1,  # Faible température pour des sorties reproductibles
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Voici l'extrait de commentaire à analyser :\n\n{chunk}"},
        ],
    }

    try:
        response = requests.post(GROQ_CHAT_URL, headers=headers, json=payload, timeout=30)

        if response.status_code != 200:
            logger.warning(f"LLM API error {response.status_code}: {response.text}")
            return [], _empty_usage()

        payload = response.json()
        usage = _extract_usage(payload)
        raw_content = payload["choices"][0]["message"]["content"]

        # Nettoyage : supprime les balises markdown ```json ... ``` si présentes
        clean_content = (
            raw_content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        parsed = json.loads(clean_content)

        # Validation et conversion en objets Pydantic
        actions = []
        for item in parsed:
            try:
                actions.append(ActionDetail(**item))
            except Exception as e:
                logger.debug(f"Action ignorée (format invalide) : {item} | {e}")

        return actions, usage

    except json.JSONDecodeError as e:
        logger.warning(f"Impossible de parser la réponse JSON du LLM : {e}")
        return [], _empty_usage()
    except requests.RequestException as e:
        logger.warning(f"Erreur réseau lors de l'appel LLM : {e}")
        return [], _empty_usage()


def analyze_transcript(
    transcript: str,
    fighter_1: str,
    fighter_2: str,
) -> tuple[list[ActionDetail], int, dict[str, int]]:
    """
    Analyse complète d'une transcription en la découpant en chunks.

    Args:
        transcript: Texte transcrit complet du commentaire audio.
        fighter_1: Nom du premier combattant.
        fighter_2: Nom du second combattant.

    Returns:
        Tuple (liste de toutes les actions détectées, nombre de chunks analysés).
    """
    # Génère le prompt système avec les noms des combattants
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        fighter_1=fighter_1,
        fighter_2=fighter_2,
    )

    chunks = split_text_into_chunks(transcript)
    all_actions: list[ActionDetail] = []
    usage_total = _empty_usage()

    logger.info(f"Analyse de {len(chunks)} chunks pour {fighter_1} vs {fighter_2}")

    for i, chunk in enumerate(chunks):
        logger.debug(f"Chunk {i + 1}/{len(chunks)}")
        actions, usage = _call_llm(chunk, system_prompt)
        all_actions.extend(actions)
        usage_total = _merge_usage(usage_total, usage)

        # Pause pour respecter les rate limits Groq (sauf après le dernier chunk)
        if i < len(chunks) - 1:
            time.sleep(RATE_LIMIT_DELAY)

    logger.info(f"Total actions détectées : {len(all_actions)}")
    return all_actions, len(chunks), usage_total


def generate_summary(transcript: str, fighter_1: str, fighter_2: str) -> tuple[str, dict[str, int]]:
    """
    Demande au LLM de générer un résumé narratif du combat en français.

    Args:
        transcript: Texte transcrit complet.
        fighter_1: Nom du premier combattant.
        fighter_2: Nom du second combattant.

    Returns:
        Résumé narratif en texte libre, ou message d'erreur.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}",
    }

    summary_prompt = f"""Tu es un journaliste sportif MMA.
En te basant sur ce commentaire de combat entre {fighter_1} et {fighter_2},
rédige un résumé narratif et dynamique du combat en 3-5 phrases en français.
Mentionne les moments-clés, le rythme et l'issue perçue du combat.
Réponds uniquement avec le texte du résumé, sans introduction ni conclusion."""

    payload = {
        "model": LLM_MODEL,
        "temperature": 0.5,
        "messages": [
            {"role": "system", "content": summary_prompt},
            {"role": "user", "content": transcript[:3000]},  # Limite pour le résumé
        ],
    }

    try:
        response = requests.post(GROQ_CHAT_URL, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            payload_json = response.json()
            usage = _extract_usage(payload_json)
            summary = payload_json["choices"][0]["message"]["content"].strip()
            return summary, usage
        return "Résumé non disponible.", _empty_usage()
    except Exception as e:
        logger.warning(f"Impossible de générer le résumé : {e}")
        return "Résumé non disponible.", _empty_usage()
