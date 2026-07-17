"""
parser.py
---------
Module 2: Resume Parser.

Provides reusable, framework-agnostic utilities to extract raw text
content from resume files. Currently supports PDF files via the
`pdfplumber` library.

This module intentionally has no dependency on Streamlit so that it
can be reused by other parts of the application (e.g., batch
processing scripts, unit tests) without pulling in UI code.
"""

import logging
from typing import Union, BinaryIO

import pdfplumber

logger = logging.getLogger(__name__)


class PDFExtractionError(Exception):
    """Raised when text cannot be extracted from a given PDF file."""


def extract_text_from_pdf(file: Union[str, BinaryIO]) -> str:
    """Extract and return all text content from a PDF resume.

    Args:
        file: A file path (str) or file-like/binary stream
            (e.g., Streamlit's UploadedFile).

    Returns:
        str: Extracted text, pages joined by newlines. Empty string
        if the PDF has no extractable text.

    Raises:
        PDFExtractionError: If the file cannot be opened or parsed.
    """
    extracted_pages: list[str] = []

    try:
        with pdfplumber.open(file) as pdf:
            if not pdf.pages:
                logger.warning("PDF contains no pages to extract text from.")
                return ""

            for page_number, page in enumerate(pdf.pages, start=1):
                try:
                    page_text = page.extract_text()
                except Exception as page_error:
                    logger.warning(
                        "Failed to extract text from page %d: %s",
                        page_number,
                        page_error,
                    )
                    page_text = None

                if page_text:
                    extracted_pages.append(page_text)

    except FileNotFoundError as exc:
        logger.error("PDF file not found: %s", exc)
        raise PDFExtractionError(f"PDF file not found: {exc}") from exc

    except Exception as exc:
        logger.error("Failed to extract text from PDF: %s", exc)
        raise PDFExtractionError(
            f"An error occurred while extracting text from the PDF: {exc}"
        ) from exc

    return "\n".join(extracted_pages)