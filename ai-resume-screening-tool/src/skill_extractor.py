"""
skill_extractor.py
-------------------
Module 4: Skill Extraction.

Provides reusable, framework-agnostic utilities to identify technical
skills mentioned in resume text by matching against a curated skills
database (`data/skills.json`).
"""

import json
import logging
import re
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

_SKILLS_JSON_PATH = Path(__file__).resolve().parent.parent / "data" / "skills.json"
print(_SKILLS_JSON_PATH)
print(_SKILLS_JSON_PATH.exists())


def load_skills(skills_path: Path = _SKILLS_JSON_PATH) -> List[str]:
    """Load and flatten the technical skills database.

    Args:
        skills_path: Path to the skills JSON file.

    Returns:
        List[str]: Flat, deduplicated list of skill names.

    Raises:
        FileNotFoundError: If the skills JSON file does not exist.
        ValueError: If the file is invalid JSON or malformed.
    """
    try:
        with open(skills_path, "r", encoding="utf-8") as skills_file:
            skills_by_category = json.load(skills_file)
    except FileNotFoundError as exc:
        logger.error("Skills database not found at: %s", skills_path)
        raise FileNotFoundError(
            f"Skills database file not found at '{skills_path}'."
        ) from exc
    except json.JSONDecodeError as exc:
        logger.error("Skills database contains invalid JSON: %s", exc)
        raise ValueError(
            f"Skills database at '{skills_path}' contains invalid JSON: {exc}"
        ) from exc

    if not isinstance(skills_by_category, dict):
        logger.error("Skills database has an unexpected top-level structure.")
        raise ValueError(
            "Skills database must be a JSON object mapping categories to "
            "lists of skill names."
        )

    all_skills: List[str] = []
    for category, skills in skills_by_category.items():
        if not isinstance(skills, list):
            logger.warning(
                "Skipping category '%s': expected a list of skills.", category
            )
            continue
        all_skills.extend(str(skill) for skill in skills)

    deduplicated: dict[str, str] = {}
    for skill in all_skills:
        key = skill.strip().lower()
        if key and key not in deduplicated:
            deduplicated[key] = skill.strip()

    skill_list = list(deduplicated.values())
    logger.info("Loaded %d unique skills from skills database.", len(skill_list))
    return skill_list


def extract_skills(text: str, skills_path: Path = _SKILLS_JSON_PATH) -> List[str]:
    """Extract technical skills mentioned in the given text.

    Args:
        text: The resume text to search for skill mentions.
        skills_path: Path to the skills JSON file.

    Returns:
        List[str]: Alphabetically sorted list of unique skills found.

    Raises:
        TypeError: If `text` is not a string.
        FileNotFoundError: If the skills database file does not exist.
        ValueError: If the skills database is malformed.
    """
    if not isinstance(text, str):
        raise TypeError(f"Expected 'text' to be a str, got {type(text).__name__}.")

    if not text.strip():
        logger.info("Received empty text; no skills to extract.")
        return []

    try:
        known_skills = load_skills(skills_path)
    except (FileNotFoundError, ValueError):
        raise

    text_lower = text.lower()
    found_skills: set[str] = set()

    try:
        for skill in known_skills:
            # Lookaround (rather than \b) reliably bounds terms
            # containing symbols like "C++", "C#", or "Node.js".
            pattern = (
                r"(?<![a-z0-9])" + re.escape(skill.lower()) + r"(?![a-z0-9])"
            )
            if re.search(pattern, text_lower):
                found_skills.add(skill)
    except re.error as exc:
        logger.error("Regex error while matching skills: %s", exc)
        raise ValueError(f"Failed to match skills against text: {exc}") from exc

    sorted_skills = sorted(found_skills, key=str.lower)
    logger.info("Extracted %d skill(s) from text.", len(sorted_skills))
    return sorted_skills