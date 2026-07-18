"""
dashboard.py
------------
Module 9: Screening Dashboard Analytics.

Provides a reusable, framework-agnostic utility that computes summary
statistics (total candidates, highest/lowest/average score, and the
top candidate) from a batch of screened candidates.

This module intentionally has no dependency on Streamlit so that it
can be reused by other parts of the application (e.g., batch
processing scripts, unit tests, reports) without pulling in UI code.
It does not generate any charts or visualizations; it only computes
the underlying summary data, leaving presentation to the caller.
"""

import logging
from typing import Any, Dict, List, Union

logger = logging.getLogger(__name__)

Number = Union[int, float]


def _validate_candidates(candidates: List[Dict[str, Any]]) -> None:
    """Validate the structure and contents of the candidates list.

    Raises:
        TypeError: If `candidates` is not a list, if any element is
            not a dict, or if a "name"/"score" value has the wrong
            type.
        ValueError: If `candidates` is empty, or if any candidate
            dictionary is missing the required "name"/"score" keys,
            or has an empty "name".
    """
    if not isinstance(candidates, list):
        raise TypeError(
            f"Expected 'candidates' to be a list, got {type(candidates).__name__}."
        )

    if not candidates:
        raise ValueError("'candidates' must not be empty.")

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

        name = candidate["name"]
        if not isinstance(name, str) or not name.strip():
            raise ValueError(
                f"Candidate at index {index} has an invalid 'name': {name!r}"
            )

        score = candidate["score"]
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            raise TypeError(
                f"Candidate '{name}' has a non-numeric score: {score!r}"
            )


def generate_dashboard(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute summary statistics for a batch of screened candidates.

    Args:
        candidates: A list of candidate dictionaries, each expected
            to contain at least:
                - "name" (str): The candidate's resume file name.
                - "score" (int | float): The candidate's match score.

    Returns:
        Dict[str, Any]: A summary dictionary containing:
            - "total_candidates" (int): The number of candidates.
            - "highest_score" (int | float): The highest match score.
            - "lowest_score" (int | float): The lowest match score.
            - "average_score" (float): The mean match score, rounded
              to two decimal places.
            - "top_candidate" (str): The name of the candidate with
              the highest score. If multiple candidates share the
              highest score, the first one encountered (in input
              order) is returned.

    Raises:
        TypeError: If `candidates` is not a list, if any element is
            not a dict, or if a "name"/"score" value has the wrong
            type.
        ValueError: If `candidates` is empty, or if any candidate
            dictionary is missing required keys or has an invalid
            "name".
    """
    _validate_candidates(candidates)

    try:
        scores: List[Number] = [candidate["score"] for candidate in candidates]

        total_candidates = len(candidates)
        highest_score = max(scores)
        lowest_score = min(scores)
        average_score = round(sum(scores) / total_candidates, 2)

        # `max` with a key returns the first candidate encountered
        # among ties, preserving input order for `top_candidate`.
        top_candidate = max(
            candidates, key=lambda candidate: candidate["score"]
        )["name"]

    except Exception as exc:
        logger.error("Failed to compute dashboard statistics: %s", exc)
        raise RuntimeError(
            f"An error occurred while computing dashboard statistics: {exc}"
        ) from exc

    summary = {
        "total_candidates": total_candidates,
        "highest_score": highest_score,
        "lowest_score": lowest_score,
        "average_score": average_score,
        "top_candidate": top_candidate,
    }

    logger.info(
        "Generated dashboard for %d candidate(s). Top candidate: '%s' (%s).",
        total_candidates,
        top_candidate,
        highest_score,
    )
    return summary