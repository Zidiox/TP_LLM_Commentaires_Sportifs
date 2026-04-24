"""
services/scorer.py
Calcul des notes finales côté serveur (Python pur, pas le LLM).
La note est déterministe, reproductible et explicable.
"""

import logging
from collections import defaultdict

from backend.config import BASE_SCORE, SCORING_COEFFICIENT
from backend.models import ActionDetail, FighterStats

logger = logging.getLogger(__name__)


def compute_scores(
    actions: list[ActionDetail],
    fighter_1: str,
    fighter_2: str,
) -> list[FighterStats]:
    """
    Calcule les statistiques et notes finales pour chaque combattant.

    Algorithme :
    - Part d'une note de base (BASE_SCORE = 5.0)
    - Additionne les points bruts × SCORING_COEFFICIENT
    - Clamp la note finale entre 0.0 et 10.0

    Args:
        actions: Liste de toutes les actions détectées par le LLM.
        fighter_1: Nom exact du premier combattant.
        fighter_2: Nom exact du second combattant.

    Returns:
        Liste de FighterStats avec les notes et statistiques calculées.
    """
    # Initialise les accumulateurs pour chaque combattant
    fighters = [fighter_1, fighter_2]
    raw_scores: dict[str, float] = {f: 0.0 for f in fighters}
    positive_points: dict[str, int] = {f: 0 for f in fighters}
    negative_points: dict[str, int] = {f: 0 for f in fighters}
    categories: dict[str, dict[str, int]] = {f: defaultdict(int) for f in fighters}

    for action in actions:
        # Normalise le nom pour faire correspondre même si la casse diffère légèrement
        matched_fighter = _match_fighter_name(action.fighter, fighters)
        if matched_fighter is None:
            logger.debug(f"Combattant non reconnu ignoré : '{action.fighter}'")
            continue

        pts = action.score
        raw_scores[matched_fighter] += pts
        categories[matched_fighter][action.category] += 1

        if pts > 0:
            positive_points[matched_fighter] += pts
        else:
            negative_points[matched_fighter] += abs(pts)

    # Calcule les notes finales
    stats_list: list[FighterStats] = []
    for fighter in fighters:
        final = BASE_SCORE + raw_scores[fighter] * SCORING_COEFFICIENT
        final = round(max(0.0, min(10.0, final)), 1)  # Clamp [0, 10]

        stats_list.append(
            FighterStats(
                name=fighter,
                final_score=final,
                total_positive_points=positive_points[fighter],
                total_negative_points=negative_points[fighter],
                actions_by_category=dict(categories[fighter]),
            )
        )

    logger.info(
        f"Scores calculés — "
        + " | ".join(f"{s.name}: {s.final_score}/10" for s in stats_list)
    )
    return stats_list


def _match_fighter_name(name: str, fighters: list[str]) -> str | None:
    """
    Tente de faire correspondre un nom retourné par le LLM avec un nom de référence.
    Utilise une correspondance insensible à la casse et partielle (recherche de token).

    Args:
        name: Nom retourné par le LLM.
        fighters: Liste des noms de référence.

    Returns:
        Le nom de référence correspondant, ou None si aucun match.
    """
    name_lower = name.lower()
    for fighter in fighters:
        # Vérifie si l'un des tokens du nom de référence apparaît dans le nom LLM
        tokens = fighter.lower().split()
        if any(token in name_lower for token in tokens):
            return fighter
    return None
