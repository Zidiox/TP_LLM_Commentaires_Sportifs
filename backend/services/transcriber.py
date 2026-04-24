"""
services/transcriber.py
Service de transcription audio → texte via l'API Whisper de Groq.
Supporte m4a, mp3, webm, wav — détection automatique du MIME type.
"""

import logging
from pathlib import Path

import requests

from backend.config import GROQ_API_KEY, GROQ_TRANSCRIPTION_URL, WHISPER_MODEL
from backend.utils.text_utils import clean_transcript

logger = logging.getLogger(__name__)

# MIME types supportés par Groq Whisper
MIME_MAP = {
    ".m4a":  "audio/mp4",
    ".mp4":  "audio/mp4",
    ".mp3":  "audio/mpeg",
    ".mpeg": "audio/mpeg",
    ".webm": "audio/webm",
    ".wav":  "audio/wav",
    ".ogg":  "audio/ogg",
}


def transcribe_audio(audio_path: Path) -> str:
    """
    Envoie un fichier audio à l'API Whisper de Groq et retourne le texte transcrit.
    Détecte automatiquement le MIME type selon l'extension du fichier.

    Args:
        audio_path: Chemin vers le fichier audio à transcrire (m4a, mp3, webm...).

    Returns:
        Texte transcrit et nettoyé.

    Raises:
        RuntimeError: Si l'API retourne une erreur ou si le fichier est inaccessible.
    """
    if not audio_path.exists():
        raise RuntimeError(f"Fichier audio introuvable : {audio_path}")

    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    mime_type = MIME_MAP.get(audio_path.suffix.lower(), "audio/mp4")

    logger.info(f"Transcription de {audio_path.name} ({mime_type})")

    try:
        with open(audio_path, "rb") as audio_file:
            files = {
                "file": (audio_path.name, audio_file, mime_type),
                "model": (None, WHISPER_MODEL),
                "response_format": (None, "json"),
                "language": (None, "en"),
            }
            response = requests.post(
                GROQ_TRANSCRIPTION_URL,
                headers=headers,
                files=files,
                timeout=120,
            )

        if response.status_code == 200:
            payload = response.json()
            raw_text = payload.get("text", "")
            cleaned = clean_transcript(raw_text)
            logger.info(f"Transcription réussie : {len(cleaned.split())} mots")
            return cleaned
        else:
            error_msg = response.json().get("error", {}).get("message", response.text)
            raise RuntimeError(f"Erreur API Whisper ({response.status_code}) : {error_msg}")

    except requests.RequestException as e:
        raise RuntimeError(f"Erreur réseau lors de la transcription : {e}") from e
