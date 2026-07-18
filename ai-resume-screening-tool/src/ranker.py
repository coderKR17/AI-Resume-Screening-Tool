"""
ranker.py
---------
Module 6: Candidate Ranking System.

Provides a reusable, framework-agnostic utility to rank candidates by
their resume match score (produced by Module 5's scoring logic),
from highest to lowest, and assign each candidate a numeric rank.

This module intentionally has no dependency on Streamlit so that it
can be reused by other parts of the application (e.g., batch
processing scripts, unit tests) without pulling in UI code.
"""

import logging
from typing import Any, Dict, List

# Module-level logger. The host application (e.g., app.py) can
# configure handlers/levels; this module only emits log records.
logger = logging.getLogger(__name__)


def rank_candidates(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Rank candidates by resume match score, highest first.

    Sorts the given list of candidates in descending order of
    `score` and assigns each candidate a 1-based `rank`. Candidates
    with equal scores are ranked according to their relative order
    in the input list (a stable sort), and receive distinct,
    consecutive rank numbers rather than being tied.

    Args:
        candidates: A list of candidate dictionaries, each expected
            to contain at least:
                - "name" (str): The candidate's resume file name.
                - "score" (int | float): The candidate's match score.

    Returns:
        List[Dict[str, Any]]: A new list of candidate dictionaries,
        sorted by descending score, where each dictionary contains:
            - "rank" (int): The candidate's 1-based rank.
            - "name" (str): The candidate's resume file name.
            - "score" (int | float): The candidate's match score.
        Returns an empty list if `candidates` is empty.

    Raises:
        TypeError: If `candidates` is not a list, or if any element
            is not a dictionary.
        ValueError: If any candidate dictionary is missing the
            required "name" or "score" keys, or if "score" is not a
            numeric value.
    """
    if not isinstance(candidates, list):
        raise TypeError(
            f"Expected 'candidates' to be a list, got {type(candidates).__name__}."
        )

    # Handle empty input gracefully; nothing to rank.
    if not candidates:
        logger.info("No candidates provided; returning empty ranking.")
        return []

    validated_candidates: List[Dict[str, Any]] = []

    for index, candidate in enumerate(candidates):
        if not isinstance(candidate, dict):
            raise TypeError(
                f"Candidate at index {index} must be a dict, "
                f"got {type(candidate).__name__}."
            )

        if "name" not in candidate or "score" not in candidate:
            raise ValueError(
                f"Candidate at index {index} is missing required "
                f"'name' and/or 'score' key(s): {candidate}"
            )

        score = candidate["score"]
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            raise ValueError(
                f"Candidate '{candidate.get('name')}' has a non-numeric "
                f"score: {score!r}"
            )

        validated_candidates.append(candidate)

    try:
        # Sort by descending score. Python's `sorted` is stable, so
        # candidates with equal scores preserve their original
        # relative order (e.g., upload order) rather than being
        # reordered arbitrarily.
        sorted_candidates = sorted(
            validated_candidates,
            key=lambda candidate: candidate["score"],
            reverse=True,
        )
    except Exception as exc:
        logger.error("Failed to sort candidates by score: %s", exc)
        raise ValueError(f"Failed to rank candidates: {exc}") from exc

    ranked_candidates: List[Dict[str, Any]] = [
        {
            "rank": position,
            "name": candidate["name"],
            "score": candidate["score"],
        }
        for position, candidate in enumerate(sorted_candidates, start=1)
    ]

    logger.info("Ranked %d candidate(s).", len(ranked_candidates))
    return ranked_candidates