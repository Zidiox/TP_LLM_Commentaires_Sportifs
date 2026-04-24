"""
main.py
Point d'entrée de l'API FastAPI.
Lance le serveur avec : uvicorn backend.main:app --reload --port 8000
"""

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.config import GROQ_API_KEY
from backend.models import AnalyzeRequest, AnalyzeResponse
from backend.services.downloader import cleanup_audio, download_audio
from backend.services.transcriber import transcribe_audio
from backend.services.analyzer import analyze_transcript, generate_summary
from backend.services.scorer import compute_scores

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifecycle & App
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Vérification de la clé API au démarrage."""
    if not GROQ_API_KEY:
        logger.error("GROQ_API_KEY manquante ! Vérifiez votre fichier .env")
    else:
        logger.info("✅ Clé API Groq chargée avec succès.")
    yield


app = FastAPI(
    title="UFC AI Judge API",
    description="Analyse audio de combats UFC via Groq Whisper + LLaMA.",
    version="1.0.0",
    lifespan=lifespan,
)

# Autorise les requêtes depuis Streamlit (localhost:8501)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health", tags=["Système"])
async def health_check():
    """Endpoint de santé pour vérifier que le serveur est actif."""
    return {
        "status": "ok",
        "groq_key_loaded": bool(GROQ_API_KEY),
    }


@app.post("/analyze", response_model=AnalyzeResponse, tags=["Analyse"])
async def analyze_fight(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    Pipeline complet d'analyse d'un combat UFC à partir d'une URL YouTube.

    Étapes :
    1. Téléchargement audio (yt-dlp)
    2. Transcription (Groq Whisper)
    3. Analyse LLM par chunks (Groq LLaMA)
    4. Calcul des scores (Python)
    5. Génération du résumé narratif
    6. Nettoyage du fichier audio temporaire
    """
    if not GROQ_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Clé API Groq non configurée. Vérifiez le fichier .env.",
        )

    audio_path = None

    try:
        # ── Étape 1 : Téléchargement ──────────────────────────────────────
        logger.info(f"[1/5] Téléchargement audio : {request.youtube_url}")
        audio_path = download_audio(request.youtube_url)

        # ── Étape 2 : Transcription ───────────────────────────────────────
        logger.info("[2/5] Transcription Whisper en cours...")
        transcript = transcribe_audio(audio_path)
        word_count = len(transcript.split())

        if not transcript.strip():
            raise HTTPException(
                status_code=422,
                detail="La transcription est vide. Vérifiez que la vidéo contient du commentaire audio.",
            )

        # ── Étape 3 : Analyse LLM ─────────────────────────────────────────
        logger.info("[3/5] Analyse LLM par chunks...")
        all_actions, chunks_count = analyze_transcript(
            transcript,
            fighter_1=request.fighter_1,
            fighter_2=request.fighter_2,
        )

        # ── Étape 4 : Scoring Python ──────────────────────────────────────
        logger.info("[4/5] Calcul des scores...")
        fighter_stats = compute_scores(
            all_actions,
            fighter_1=request.fighter_1,
            fighter_2=request.fighter_2,
        )

        # ── Étape 5 : Résumé narratif ─────────────────────────────────────
        logger.info("[5/5] Génération du résumé...")
        summary = generate_summary(transcript, request.fighter_1, request.fighter_2)

        return AnalyzeResponse(
            success=True,
            transcript=transcript,
            transcript_word_count=word_count,
            chunks_analyzed=chunks_count,
            all_actions=all_actions,
            fighter_stats=fighter_stats,
            summary=summary,
        )

    except HTTPException:
        raise
    except RuntimeError as e:
        logger.error(f"Erreur métier : {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.exception(f"Erreur inattendue : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur interne : {e}")
    finally:
        # ── Nettoyage : toujours supprimer le MP3 temporaire ──────────────
        if audio_path is not None:
            cleanup_audio(audio_path)
            logger.info("Fichier audio temporaire supprimé.")
