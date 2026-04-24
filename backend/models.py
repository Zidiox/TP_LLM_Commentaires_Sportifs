"""
models.py
Schémas Pydantic pour la validation des requêtes et réponses de l'API.
"""

from pydantic import BaseModel, HttpUrl, field_validator
from typing import Optional


# ---------------------------------------------------------------------------
# Requête
# ---------------------------------------------------------------------------

class AnalyzeRequest(BaseModel):
    """Payload envoyé par le frontend pour lancer une analyse."""
    youtube_url: str
    fighter_1: str = "Khabib Nurmagomedov"
    fighter_2: str = "Conor McGregor"

    @field_validator("youtube_url")
    @classmethod
    def must_be_youtube(cls, v: str) -> str:
        if "youtube.com" not in v and "youtu.be" not in v:
            raise ValueError("L'URL doit être une URL YouTube valide.")
        return v

    @field_validator("fighter_1", "fighter_2")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Le nom du combattant ne peut pas être vide.")
        return v.strip()


# ---------------------------------------------------------------------------
# Sous-modèles de réponse
# ---------------------------------------------------------------------------

class ActionDetail(BaseModel):
    """Une action individuelle détectée par le LLM."""
    fighter: str
    action: str
    category: str
    score: int


class FighterStats(BaseModel):
    """Statistiques agrégées pour un combattant."""
    name: str
    final_score: float
    total_positive_points: int
    total_negative_points: int
    actions_by_category: dict[str, int]  # {"takedown": 3, "strike": 7, ...}


class AnalyzeResponse(BaseModel):
    """Réponse complète renvoyée au frontend après une analyse."""
    success: bool
    transcript: str
    transcript_word_count: int
    chunks_analyzed: int
    all_actions: list[ActionDetail]
    fighter_stats: list[FighterStats]
    summary: Optional[str] = None
    error: Optional[str] = None
