"""
exporter.py
-----------
Module 10: CSV Export.

Provides a reusable, framework-agnostic utility that converts a list
of ranked candidates into a CSV file, returned as raw bytes.

This module intentionally has no dependency on Streamlit so that it
can be reused by other parts of the application (e.g., batch export
scripts, unit tests) without pulling in UI code. It returns the CSV
as bytes rather than writing to disk, leaving persistence (e.g.,
`st.download_button`) to the caller.
"""

import logging
from typing import Any, Dict, List

import pandas as pd

logger = logging.getLogger(__name__)

_CSV_ENCODING = "utf-8-sig"


class CSVExportError(Exception):
    """Raised when ranked candidate results cannot be exported to CSV."""


def _validate_ranked_candidates(ranked_candidates: List[Dict[str, Any]]) -> None:
    """Validate the structure and contents of the ranked candidates list.

    Raises:
        TypeError: If `ranked_candidates` is not a list, or if any
            element is not a dict.
        ValueError: If `ranked_candidates` is empty, or if any
            candidate dictionary is missing required keys.
    """
    if not isinstance(ranked_candidates, list):
        raise TypeError(
            "Expected 'ranked_candidates' to be a list, got "
            f"{type(ranked_candidates).__name__}."
        )

    if not ranked_candidates:
        raise ValueError("'ranked_candidates' must not be empty.")

    required_keys = {"rank", "name", "score"}

    for index, candidate in enumerate(ranked_candidates):
        if not isinstance(candidate, dict):
            raise TypeError(
                f"Candidate at index {index} must be a dict, "
                f"got {type(candidate).__name__}."
            )

        missing_keys = required_keys - candidate.keys()
        if missing_keys:
            raise ValueError(
                f"Candidate at index {index} is missing required "
                f"key(s) {sorted(missing_keys)}: {candidate}"
            )


def export_results_to_csv(ranked_candidates: List[Dict[str, Any]]) -> bytes:
    """Export ranked candidate results to CSV, returned as bytes.

    Converts a list of ranked candidate dictionaries (as produced by
    `src.ranker.rank_candidates`) into a CSV file with columns
    "rank", "name", and "score", encoded as UTF-8 (with BOM) bytes so
    the file opens correctly in Excel and other spreadsheet tools.

    Args:
        ranked_candidates: A list of candidate dictionaries, each
            expected to contain at least:
                - "rank" (int): The candidate's 1-based rank.
                - "name" (str): The candidate's resume file name.
                - "score" (int | float): The candidate's match score.

    Returns:
        bytes: The generated CSV file content as raw bytes, suitable
        for writing to disk or passing to `st.download_button`.

    Raises:
        TypeError: If `ranked_candidates` is not a list, or if any
            element is not a dict.
        ValueError: If `ranked_candidates` is empty, or if any
            candidate dictionary is missing required keys.
        CSVExportError: If CSV generation fails for any other reason.
    """
    _validate_ranked_candidates(ranked_candidates)

    try:
        dataframe = pd.DataFrame(ranked_candidates)

        # Ensure a consistent, predictable column order regardless of
        # key insertion order in the input dictionaries. Any extra
        # columns beyond the required three are preserved and appended
        # at the end, rather than silently dropped.
        ordered_columns = ["rank", "name", "score"]
        remaining_columns = [
            column for column in dataframe.columns if column not in ordered_columns
        ]
        dataframe = dataframe[ordered_columns + remaining_columns]

        csv_string = dataframe.to_csv(index=False)
        csv_bytes = csv_string.encode(_CSV_ENCODING)

    except (TypeError, ValueError):
        raise

    except Exception as exc:
        logger.error("Failed to export ranked candidates to CSV: %s", exc)
        raise CSVExportError(
            f"An error occurred while exporting results to CSV: {exc}"
        ) from exc

    logger.info(
        "Exported %d candidate(s) to CSV (%d bytes).",
        len(ranked_candidates),
        len(csv_bytes),
    )
    return csv_bytes