"""
report_generator.py
--------------------
Module 8: PDF Report Generation.

Provides a reusable, framework-agnostic utility that renders a single
candidate's resume screening results (match score, rank, skills, and
improvement suggestions) into a downloadable PDF report, using
`reportlab`.

This module intentionally has no dependency on Streamlit so that it
can be reused by other parts of the application (e.g., batch export
scripts, unit tests) without pulling in UI code. It returns the PDF
as raw bytes rather than writing to disk, leaving persistence (e.g.,
`st.download_button`) to the caller.
"""

import logging
from datetime import datetime
from io import BytesIO
from typing import List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

logger = logging.getLogger(__name__)

_MIN_SCORE = 0
_MAX_SCORE = 100

_NO_MATCHED_SKILLS_TEXT = "No matched skills found."
_NO_MISSING_SKILLS_TEXT = "No missing skills found."
_NO_SUGGESTIONS_TEXT = "No suggestions available."

_REPORT_TITLE = "AI Resume Screening Report"
_PAGE_MARGIN_CM = 2


class ReportGenerationError(Exception):
    """Raised when a PDF report cannot be generated."""


def _validate_inputs(
    candidate_name: str,
    score: int,
    matched_skills: List[str],
    missing_skills: List[str],
    suggestions: List[str],
    rank: Optional[int],
) -> None:
    """Validate all inputs to `generate_pdf_report`.

    Raises:
        TypeError: If any argument has an unexpected type.
        ValueError: If `candidate_name` is empty/blank, `score` is
            outside the expected 0-100 range, or `rank` is not a
            positive integer when provided.
    """
    if not isinstance(candidate_name, str) or not candidate_name.strip():
        raise ValueError("'candidate_name' must be a non-empty string.")

    if isinstance(score, bool) or not isinstance(score, (int, float)):
        raise TypeError(f"Expected 'score' to be numeric, got {type(score).__name__}.")

    if not (_MIN_SCORE <= score <= _MAX_SCORE):
        raise ValueError(
            f"'score' must be between {_MIN_SCORE} and {_MAX_SCORE}, got {score}."
        )

    for name, value in (
        ("matched_skills", matched_skills),
        ("missing_skills", missing_skills),
        ("suggestions", suggestions),
    ):
        if not isinstance(value, list) or not all(
            isinstance(item, str) for item in value
        ):
            raise TypeError(f"'{name}' must be a list of strings.")

    if rank is not None:
        if isinstance(rank, bool) or not isinstance(rank, int):
            raise TypeError(
                f"Expected 'rank' to be an int or None, got {type(rank).__name__}."
            )
        if rank < 1:
            raise ValueError(f"'rank' must be a positive integer, got {rank}.")


def _build_bullet_list(items: List[str], style: ParagraphStyle) -> ListFlowable:
    """Build a reportlab bulleted list flowable from a list of strings."""
    list_items = [
        ListItem(Paragraph(item, style), leftIndent=12) for item in items
    ]
    return ListFlowable(
        list_items,
        bulletType="bullet",
        start="circle",
        leftIndent=18,
    )


def generate_pdf_report(
    candidate_name: str,
    score: int,
    matched_skills: List[str],
    missing_skills: List[str],
    suggestions: List[str],
    rank: Optional[int] = None,
) -> bytes:
    """Generate a PDF resume screening report for a single candidate.

    Args:
        candidate_name: The candidate's name or resume file name.
        score: The candidate's job-description match score (0-100).
        matched_skills: Skills present in both the resume and job
            description.
        missing_skills: Skills required by the job description but
            missing from the resume.
        suggestions: Resume improvement suggestions for the candidate.
        rank: The candidate's rank among all screened candidates.
            Defaults to None if ranking has not been performed.

    Returns:
        bytes: The generated PDF document as raw bytes.

    Raises:
        TypeError: If any argument has an unexpected type.
        ValueError: If `candidate_name` is empty, `score` is out of
            range, or `rank` is not a positive integer when provided.
        ReportGenerationError: If PDF rendering fails for any other
            reason.
    """
    _validate_inputs(
        candidate_name, score, matched_skills, missing_skills, suggestions, rank
    )

    try:
        buffer = BytesIO()
        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=_PAGE_MARGIN_CM * cm,
            bottomMargin=_PAGE_MARGIN_CM * cm,
            leftMargin=_PAGE_MARGIN_CM * cm,
            rightMargin=_PAGE_MARGIN_CM * cm,
            title=_REPORT_TITLE,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "ReportTitle", parent=styles["Title"], fontSize=20, spaceAfter=6,
        )
        section_heading_style = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            spaceBefore=14,
            spaceAfter=6,
            textColor=colors.HexColor("#1F3864"),
        )
        body_style = ParagraphStyle(
            "Body", parent=styles["Normal"], fontSize=11, leading=15,
        )
        meta_style = ParagraphStyle(
            "Meta", parent=styles["Normal"], fontSize=9, textColor=colors.grey,
        )

        story = []

        story.append(Paragraph(_REPORT_TITLE, title_style))
        generated_at = datetime.now().strftime("%d %B %Y, %I:%M %p")
        story.append(Paragraph(f"Generated on: {generated_at}", meta_style))
        story.append(Spacer(1, 12))

        story.append(Paragraph("Candidate Summary", section_heading_style))
        story.append(
            Paragraph(f"<b>Candidate Name:</b> {candidate_name}", body_style)
        )
        story.append(Paragraph(f"<b>Match Score:</b> {score}/100", body_style))
        if rank is not None:
            story.append(Paragraph(f"<b>Candidate Rank:</b> #{rank}", body_style))

        story.append(Paragraph("Matched Skills", section_heading_style))
        if matched_skills:
            story.append(_build_bullet_list(matched_skills, body_style))
        else:
            story.append(Paragraph(_NO_MATCHED_SKILLS_TEXT, body_style))

        story.append(Paragraph("Missing Skills", section_heading_style))
        if missing_skills:
            story.append(_build_bullet_list(missing_skills, body_style))
        else:
            story.append(Paragraph(_NO_MISSING_SKILLS_TEXT, body_style))

        story.append(
            Paragraph("Resume Improvement Suggestions", section_heading_style)
        )
        if suggestions:
            story.append(_build_bullet_list(suggestions, body_style))
        else:
            story.append(Paragraph(_NO_SUGGESTIONS_TEXT, body_style))

        document.build(story)

        pdf_bytes = buffer.getvalue()
        buffer.close()

        logger.info(
            "Generated PDF report for candidate '%s' (%d bytes).",
            candidate_name,
            len(pdf_bytes),
        )
        return pdf_bytes

    except (TypeError, ValueError):
        raise

    except Exception as exc:
        logger.error(
            "Failed to generate PDF report for candidate '%s': %s",
            candidate_name,
            exc,
        )
        raise ReportGenerationError(
            f"An error occurred while generating the PDF report: {exc}"
        ) from exc