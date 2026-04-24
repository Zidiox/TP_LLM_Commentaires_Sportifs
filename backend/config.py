"""
config.py
Chargement des variables d'environnement et constantes globales de l'application.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Charge le fichier .env situé à la racine du projet
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

# --- Clés API ---
GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")

# --- Modèles Groq ---
WHISPER_MODEL: str = "whisper-large-v3"
LLM_MODEL: str = "llama-3.3-70b-versatile"

# --- Paramètres de découpage du texte ---
WORDS_PER_CHUNK: int = 150

# --- Dossier temporaire pour les fichiers audio ---
TEMP_DIR: Path = Path(__file__).parent.parent / "temp"
TEMP_DIR.mkdir(exist_ok=True)

# --- URLs des APIs Groq ---
GROQ_TRANSCRIPTION_URL: str = "https://api.groq.com/openai/v1/audio/transcriptions"
GROQ_CHAT_URL: str = "https://api.groq.com/openai/v1/chat/completions"

# --- Barème de scoring (utilisé dans scorer.py) ---
SCORING_RULES: dict[str, int] = {
    "ko":           5,
    "submission":   5,
    "takedown":     3,
    "strike":       2,
    "defense":      1,
    "strike_taken": -1,
    "takedown_taken": -2,
    "ko_taken":     -5,
    "submission_taken": -5,
}

# Note de départ pour chaque combattant (base neutre)
BASE_SCORE: float = 5.0

# Coefficient appliqué à chaque point LLM pour normaliser la note finale
SCORING_COEFFICIENT: float = 0.05

# --- Prompt système pour le LLM ---
SYSTEM_PROMPT_TEMPLATE: str = """Tu es un expert en analyse de MMA/UFC.
Ta mission est d'analyser un extrait de commentaire audio d'un combat et d'en extraire les actions clés.

Les combattants sont : {fighter_1} et {fighter_2}.

Pour chaque action identifiée, attribue un score selon ce barème STRICT :
- KO ou soumission réussie : +5
- Takedown réussi : +3
- Frappe significative : +2
- Bonne défense : +1
- Coup subi : -1
- Takedown subi : -2
- KO ou soumission subie : -5

Tu dois aussi identifier la catégorie de chaque action parmi :
"ko", "submission", "takedown", "strike", "defense", "strike_taken", "takedown_taken", "ko_taken", "submission_taken"

RÈGLES ABSOLUES :
1. Réponds UNIQUEMENT avec un tableau JSON valide, sans texte avant ou après.
2. Si aucune action n'est identifiable, réponds avec un tableau vide : []
3. Utilise EXACTEMENT les noms "{fighter_1}" et "{fighter_2}" dans le champ "fighter".

Format de sortie attendu :
[
  {{
    "fighter": "Nom exact du combattant",
    "action": "Description courte de l'action",
    "category": "categorie_action",
    "score": valeur_numerique
  }}
]"""
