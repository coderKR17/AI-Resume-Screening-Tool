"""
app.py
------
AI Resume Screening Tool
"""

import logging

import streamlit as st

from src.parser import PDFExtractionError, extract_text_from_pdf
from src.preprocessing import preprocess_resume
from src.skill_extractor import extract_skills
from src.scorer import calculate_match_score

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ALLOWED_FILE_TYPES = ["pdf"]


def configure_page():
    st.set_page_config(
        page_title="AI Resume Screening Tool",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def render_title():
    st.title("AI Resume Screening Tool")


def render_resume_uploader():

    st.subheader("Upload Resume")

    uploaded_file = st.file_uploader(
        "Upload a resume (PDF only)",
        type=ALLOWED_FILE_TYPES,
    )

    if uploaded_file is None:
        return

    # ---------------- Module 2 ----------------

    with st.spinner("Extracting text from resume..."):
        try:
            extracted_text = extract_text_from_pdf(uploaded_file)
        except PDFExtractionError as error:
            st.error(error)
            return

    if not extracted_text.strip():
        st.warning("No text found in resume.")
        return

    st.success(f"Resume '{uploaded_file.name}' processed successfully!")

    with st.expander("View Extracted Resume Text"):
        st.text_area(
            "Extracted Text",
            extracted_text,
            height=350,
            disabled=True,
        )

    # ---------------- Module 3 ----------------

    with st.spinner("Cleaning resume..."):
        cleaned_text = preprocess_resume(extracted_text)

    with st.expander("Cleaned Resume Text"):
        st.text_area(
            "Cleaned Text",
            cleaned_text,
            height=350,
            disabled=True,
        )

    # ---------------- Module 4 ----------------

    st.subheader("Extracted Skills")

    try:
        detected_skills = extract_skills(cleaned_text)
    except Exception as e:
        st.error(e)
        return

    if detected_skills:
        for skill in detected_skills:
            st.success(skill)
    else:
        st.warning("No technical skills detected.")

    # ---------------- Module 5 ----------------

    st.subheader("Job Description")

    job_description = st.text_area(
        "Paste the Job Description here",
        height=200,
        placeholder="Example: Looking for a Python Developer with SQL, Machine Learning, Git, Docker..."
    )

    if job_description.strip():

        score, matched_skills, missing_skills = calculate_match_score(
            detected_skills,
            job_description
        )

        st.subheader("Resume Match Score")

        st.progress(score / 100)

        st.success(f"Match Score: {score}%")

        st.subheader("Matched Skills")

        if matched_skills:
            for skill in matched_skills:
                st.success(f"✅ {skill}")
        else:
            st.warning("No matched skills found.")

        st.subheader("Missing Skills")

        if missing_skills:
            for skill in missing_skills:
                st.error(f"❌ {skill}")
        else:
            st.success("All required skills matched.")


def main():
    configure_page()
    render_title()
    render_resume_uploader()


if __name__ == "__main__":
    main()
