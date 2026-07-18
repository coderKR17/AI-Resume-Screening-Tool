"""
suggestions.py
--------------
Module 7: Resume Improvement Suggestions.

Provides a reusable, framework-agnostic utility that generates
actionable resume improvement suggestions based on a candidate's
job-description match score, matched skills, and missing skills.

This module intentionally has no dependency on Streamlit so that it
can be reused by other parts of the application (e.g., batch
processing scripts, unit tests, reports) without pulling in UI code.
"""

import logging
from typing import List

logger = logging.getLogger(__name__)

_EXCELLENT_SCORE_THRESHOLD = 90
_GOOD_SCORE_THRESHOLD = 70

_MIN_SCORE = 0
_MAX_SCORE = 100

_SKILL_SUGGESTION_TEMPLATES = {
    "docker": "Learn Docker and add it to your resume.",
    "kubernetes": "Learn Kubernetes for container orchestration.",
    "aws": "Gain experience with AWS cloud services.",
    "azure": "Gain experience with Microsoft Azure cloud services.",
    "google cloud": "Gain experience with Google Cloud Platform.",
    "machine learning": "Build a Machine Learning project.",
    "deep learning": "Build a Deep Learning project to strengthen your profile.",
    "nlp": "Work on an NLP project to demonstrate practical skills.",
    "computer vision": "Build a Computer Vision project for your portfolio.",
    "sql": "Strengthen your SQL and database querying skills.",
    "git": "Use Git for version control in your projects.",
    "react": "Build a project using React to showcase frontend skills.",
    "django": "Build a project using Django to showcase backend skills.",
    "flask": "Build a project using Flask to showcase backend skills.",
    "tensorflow": "Build a project using TensorFlow.",
    "pytorch": "Build a project using PyTorch.",
    "linux": "Get comfortable working in a Linux environment.",
    "ci/cd": "Learn CI/CD pipelines to demonstrate DevOps readiness.",
}

_DEFAULT_SKILL_TEMPLATE = "Gain experience with {skill} and add it to your resume."

_EXCELLENT_SCORE_SUGGESTIONS: List[str] = [
    "Excellent resume.",
    "Keep your skills updated.",
    "Continue building strong projects.",
]

_GOOD_SCORE_GENERAL_SUGGESTIONS: List[str] = [
    "Add measurable achievements to strengthen your resume.",
    "Ensure your resume formatting is clean and consistent.",
]

_LOW_SCORE_GENERAL_SUGGESTIONS: List[str] = [
    "Work on stronger, real-world projects to demonstrate your skills.",
    "Consider earning relevant certifications to strengthen your profile.",
    "Include GitHub or Portfolio links.",
    "Add your LinkedIn profile to your resume.",
    "Keep your resume ATS-friendly.",
    "Add measurable, quantified achievements to your resume.",
]


def _build_missing_skill_suggestions(missing_skills: List[str]) -> List[str]:
    """Build one suggestion string per missing skill.

    Looks up each skill (case-insensitively) in the known skill
    suggestion templates, falling back to a generic template for
    skills without a dedicated phrasing. Duplicate skills (by
    case-insensitive comparison) are only suggested once, and order
    of first appearance is preserved.

    Args:
        missing_skills: List of skill names the candidate is missing.

    Returns:
        List[str]: One suggestion sentence per unique missing skill.
    """
    suggestions: List[str] = []
    seen_skills: set[str] = set()

    for skill in missing_skills:
        if not isinstance(skill, str) or not skill.strip():
            logger.warning("Skipping invalid missing skill entry: %r", skill)
            continue

        normalized = skill.strip()
        dedup_key = normalized.lower()
        if dedup_key in seen_skills:
            continue
        seen_skills.add(dedup_key)

        template = _SKILL_SUGGESTION_TEMPLATES.get(dedup_key)
        if template:
            suggestions.append(template)
        else:
            suggestions.append(_DEFAULT_SKILL_TEMPLATE.format(skill=normalized))

    return suggestions


def generate_resume_suggestions(
    match_score: float,
    matched_skills: List[str],
    missing_skills: List[str],
) -> List[str]:
    """Generate actionable resume improvement suggestions.

    The suggestions returned depend on the candidate's match score:
        - score >= 90: Only positive, encouraging suggestions.
        - 70 <= score < 90: Missing-skill suggestions plus a small
          set of general resume-improvement tips.
        - score < 70: Missing-skill suggestions plus a comprehensive
          set of resume-improvement tips (projects, certifications,
          GitHub/LinkedIn presence, ATS formatting, quantified
          achievements).

    Args:
        match_score: The candidate's job-description match score,
            expected to be a numeric value on a 0-100 scale.
        matched_skills: List of skills the candidate already has that
            matched the job description. Currently used for
            validation/logging; reserved for future personalization.
        missing_skills: List of skills required by the job description
            but not found in the candidate's resume.

    Returns:
        List[str]: An ordered list of human-readable suggestion
        strings tailored to the candidate's match score.

    Raises:
        TypeError: If `match_score` is not numeric, or if
            `matched_skills`/`missing_skills` are not lists of
            strings.
    """
    if isinstance(match_score, bool) or not isinstance(match_score, (int, float)):
        raise TypeError(
            f"Expected 'match_score' to be numeric, got {type(match_score).__name__}."
        )

    if not isinstance(matched_skills, list) or not all(
        isinstance(skill, str) for skill in matched_skills
    ):
        raise TypeError("Expected 'matched_skills' to be a list of strings.")

    if not isinstance(missing_skills, list) or not all(
        isinstance(skill, str) for skill in missing_skills
    ):
        raise TypeError("Expected 'missing_skills' to be a list of strings.")

    if not (_MIN_SCORE <= match_score <= _MAX_SCORE):
        logger.warning(
            "match_score %s is outside the expected %d-%d range.",
            match_score,
            _MIN_SCORE,
            _MAX_SCORE,
        )

    try:
        if match_score >= _EXCELLENT_SCORE_THRESHOLD:
            logger.info(
                "Score %.2f is excellent; returning positive-only suggestions.",
                match_score,
            )
            return list(_EXCELLENT_SCORE_SUGGESTIONS)

        if match_score >= _GOOD_SCORE_THRESHOLD:
            logger.info(
                "Score %.2f is good; suggesting missing skills and "
                "light resume improvements.",
                match_score,
            )
            suggestions = _build_missing_skill_suggestions(missing_skills)
            suggestions.extend(_GOOD_SCORE_GENERAL_SUGGESTIONS)
            return suggestions

        logger.info(
            "Score %.2f is low; suggesting missing skills and "
            "comprehensive resume improvements.",
            match_score,
        )
        suggestions = _build_missing_skill_suggestions(missing_skills)
        suggestions.extend(_LOW_SCORE_GENERAL_SUGGESTIONS)
        return suggestions

    except Exception as exc:
        logger.error("Failed to generate resume suggestions: %s", exc)
        raise RuntimeError(
            f"An error occurred while generating resume suggestions: {exc}"
        ) from exc