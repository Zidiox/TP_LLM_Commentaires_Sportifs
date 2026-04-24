"""
utils/text_utils.py
Utilitaires pour le traitement et le découpage du texte transcrit.
"""

from backend.config import WORDS_PER_CHUNK


def split_text_into_chunks(text: str, words_per_chunk: int = WORDS_PER_CHUNK) -> list[str]:
    """
    Découpe un texte long en morceaux de taille fixe (en nombre de mots).

    Args:
        text: Le texte brut à découper.
        words_per_chunk: Nombre de mots par chunk.

    Returns:
        Liste de chaînes de caractères (chunks).
    """
    words = text.split()
    chunks = [
        " ".join(words[i : i + words_per_chunk])
        for i in range(0, len(words), words_per_chunk)
    ]
    # Filtre les chunks vides
    return [chunk for chunk in chunks if chunk.strip()]


def clean_transcript(text: str) -> str:
    """
    Nettoie légèrement un texte transcrit automatiquement.
    - Supprime les espaces multiples
    - Corrige les sauts de ligne excessifs

    Args:
        text: Texte brut sorti du modèle STT.

    Returns:
        Texte nettoyé.
    """
    import re
    # Remplace les séquences de whitespace multiples par un seul espace
    text = re.sub(r"\s+", " ", text)
    return text.strip()
