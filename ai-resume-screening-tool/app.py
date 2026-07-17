"""
app.py
------
Entry point for the AI-Powered Smart Resume Screening and Candidate
Ranking Tool.

Module 2 adds resume upload + text extraction functionality.
Run with: streamlit run app.py
"""

import logging

import streamlit as st

from src.parser import PDFExtractionError, extract_text_from_pdf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ALLOWED_FILE_TYPES: list[str] = ["pdf"]


def configure_page() -> None:
    """Configure global Streamlit page settings."""
    st.set_page_config(
        page_title="AI Resume Screening Tool",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def render_title() -> None:
    """Render the main application title."""
    st.title("AI Resume Screening Tool")


def render_resume_uploader() -> None:
    """Render the resume uploader and handle text extraction."""
    st.subheader("Upload Resume")

    uploaded_file = st.file_uploader(
        label="Upload a resume (PDF only)",
        type=ALLOWED_FILE_TYPES,
        accept_multiple_files=False,
        help="Only PDF files are supported at this stage.",
    )

    if uploaded_file is None:
        return

    with st.spinner("Extracting text from resume..."):
        try:
            extracted_text = extract_text_from_pdf(uploaded_file)
        except PDFExtractionError as error:
            logger.error("Resume text extraction failed: %s", error)
            st.error(f"Could not extract text from this PDF: {error}")
            return
        except Exception:
            logger.exception("Unexpected error during resume parsing.")
            st.error("An unexpected error occurred while processing the file.")
            return

    if not extracted_text.strip():
        st.warning(
            "The resume was processed, but no text could be found. "
            "It may be a scanned/image-based PDF."
        )
        return

    st.success(f"Resume '{uploaded_file.name}' processed successfully!")

    with st.expander("View Extracted Resume Text", expanded=False):
        st.text_area(
            label="Extracted Text",
            value=extracted_text,
            height=400,
            disabled=True,
        )


def main() -> None:
    """Application entry point."""
    configure_page()
    render_title()
    render_resume_uploader()


if __name__ == "__main__":
    main()
