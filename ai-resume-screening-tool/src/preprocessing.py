"""
preprocessing.py
-----------------
Module 3: Text Preprocessing.

Provides reusable, framework-agnostic text-cleaning utilities used to
normalize raw resume text extracted by `src.parser` before it is fed
into downstream NLP/ranking models.

This module intentionally has no dependency on Streamlit so that it
can be reused by other parts of the application (e.g., batch
processing scripts, unit tests) without pulling in UI code.
"""

import logging
import re
import string

import nltk
from nltk.corpus import stopwords

logger = logging.getLogger(__name__)

_NLTK_STOPWORDS_RESOURCE = "corpora/stopwords"
_NLTK_STOPWORDS_PACKAGE = "stopwords"


def _ensure_nltk_stopwords_available() -> None:
    """Ensure the NLTK 'stopwords' corpus is downloaded locally.

    Raises:
        RuntimeError: If the corpus cannot be located or downloaded.
    """
    try:
        nltk.data.find(_NLTK_STOPWORDS_RESOURCE)
    except LookupError:
        try:
            logger.info("NLTK 'stopwords' corpus not found. Downloading...")
            nltk.download(_NLTK_STOPWORDS_PACKAGE, quiet=True)
            nltk.data.find(_NLTK_STOPWORDS_RESOURCE)
        except Exception as exc:
            logger.error("Failed to download NLTK 'stopwords' corpus: %s", exc)
            raise RuntimeError(
                "NLTK 'stopwords' corpus is unavailable and could not be "
                "downloaded automatically. Please run "
                "`python -m nltk.downloader stopwords` manually."
            ) from exc


def clean_text(text: str) -> str:
    """Normalize raw text by lowercasing and stripping noise.

    Steps applied, in order:
        1. Lowercase.
        2. Remove punctuation.
        3. Remove digits/numbers.
        4. Remove special/non-alphanumeric characters.
        5. Collapse whitespace and trim.

    Args:
        text: The raw input text to clean.

    Returns:
        str: The cleaned text (empty string if input is empty/blank).

    Raises:
        TypeError: If `text` is not a string.
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected 'text' to be a str, got {type(text).__name__}.")

    if not text.strip():
        return ""

    try:
        cleaned = text.lower()
        cleaned = cleaned.translate(str.maketrans("", "", string.punctuation))
        cleaned = re.sub(r"\d+", " ", cleaned)
        cleaned = re.sub(r"[^a-z\s]", " ", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned
    except Exception as exc:
        logger.error("Failed to clean text: %s", exc)
        raise RuntimeError(f"An error occurred while cleaning text: {exc}") from exc


def remove_stopwords(text: str) -> str:
    """Remove common English stopwords from the given text.

    Args:
        text: Input text (ideally pre-cleaned via `clean_text`).

    Returns:
        str: Text with stopwords removed.

    Raises:
        TypeError: If `text` is not a string.
        RuntimeError: If the NLTK stopwords corpus is unavailable.
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected 'text' to be a str, got {type(text).__name__}.")

    if not text.strip():
        return ""

    try:
        _ensure_nltk_stopwords_available()
        english_stopwords = set(stopwords.words("english"))
        tokens = text.split()
        filtered_tokens = [t for t in tokens if t not in english_stopwords]
        return " ".join(filtered_tokens)
    except RuntimeError:
        raise
    except Exception as exc:
        logger.error("Failed to remove stopwords: %s", exc)
        raise RuntimeError(
            f"An error occurred while removing stopwords: {exc}"
        ) from exc


def preprocess_resume(text: str) -> str:
    """Run the full preprocessing pipeline on raw resume text.

    Combines `clean_text` and `remove_stopwords`.

    Args:
        text: Raw resume text, typically from
            `src.parser.extract_text_from_pdf`.

    Returns:
        str: Fully cleaned and stopword-filtered text.

    Raises:
        RuntimeError: If any pipeline stage fails unexpectedly.
    """
    if not isinstance(text, str) or not text.strip():
        logger.warning("preprocess_resume received empty or invalid input.")
        return ""

    try:
        cleaned = clean_text(text)
        without_stopwords = remove_stopwords(cleaned)
        return without_stopwords
    except Exception as exc:
        logger.error("Resume preprocessing pipeline failed: %s", exc)
        raise RuntimeError(
            f"An error occurred while preprocessing the resume: {exc}"
        ) from exc