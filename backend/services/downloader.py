"""
services/downloader.py
Téléchargement audio YouTube sans conversion ffmpeg.
Utilise le format le plus permissif pour maximiser la compatibilité.
"""

import uuid
import logging
from pathlib import Path

import yt_dlp

from backend.config import TEMP_DIR

logger = logging.getLogger(__name__)


def download_audio(youtube_url: str) -> Path:
    """
    Télécharge la piste audio d'une vidéo YouTube sans ffmpeg.
    Utilise une stratégie de fallback de formats pour éviter les erreurs
    "Requested format is not available" sur certaines vidéos.
    """
    unique_id = uuid.uuid4().hex[:8]
    output_template = str(TEMP_DIR / f"audio_{unique_id}.%(ext)s")

    ydl_opts = {
        # Fallback robuste:
        # 1) meilleur flux audio-only
        # 2) meilleur flux contenant un codec audio
        # 3) meilleur flux disponible
        "format": "bestaudio[acodec!=none]/best[acodec!=none]/best",
        "outtmpl": output_template,
        "quiet": False,   # Logs visibles pour debugger
        "no_warnings": False,
        "noplaylist": True,
        "postprocessors": [],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])

        candidates = sorted(TEMP_DIR.glob(f"audio_{unique_id}.*"))
        if not candidates:
            raise RuntimeError("Le fichier audio n'a pas été créé par yt-dlp.")

        output_path = candidates[0]
        logger.info(f"Audio téléchargé : {output_path} ({output_path.stat().st_size // 1024} Ko)")
        return output_path

    except yt_dlp.utils.DownloadError as e:
        raise RuntimeError(f"Échec du téléchargement audio : {e}") from e


def cleanup_audio(file_path: Path) -> None:
    try:
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Fichier temporaire supprimé : {file_path}")
    except OSError as e:
        logger.warning(f"Impossible de supprimer {file_path} : {e}")