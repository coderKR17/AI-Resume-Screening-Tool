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
import pandas as pd
from src.ranker import rank_candidates

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

    uploaded_files = st.file_uploader(
        "Upload Resume(s) (PDF only)",
        type=ALLOWED_FILE_TYPES,
        accept_multiple_files=True,
    )

    if not uploaded_files:
        return

    # ---------------- Job Description ----------------

    st.subheader("Job Description")

    job_description = st.text_area(
        "Paste the Job Description here",
        height=200,
        placeholder="Example: Looking for a Python Developer with SQL, Machine Learning, Git, Docker...",
    )

    if not job_description.strip():
        return

    # List for Module 6
    candidates = []

    # ==================================================
    # Process every uploaded resume
    # ==================================================

    for uploaded_file in uploaded_files:

        # ---------------- Module 2 ----------------

        with st.spinner("Extracting text from resume..."):
            try:
                extracted_text = extract_text_from_pdf(uploaded_file)
            except PDFExtractionError as error:
                st.error(error)
                continue

        if not extracted_text.strip():
            st.warning(f"No text found in {uploaded_file.name}.")
            continue

        st.success(f"Resume '{uploaded_file.name}' processed successfully!")

        with st.expander(f"View Extracted Resume Text - {uploaded_file.name}"):
            st.text_area(
                "Extracted Text",
                extracted_text,
                height=350,
                disabled=True,
            )
                   # ---------------- Module 3 ----------------

        with st.spinner("Cleaning resume..."):
            cleaned_text = preprocess_resume(extracted_text)

        with st.expander(f"Cleaned Resume Text - {uploaded_file.name}"):
            st.text_area(
                "Cleaned Text",
                cleaned_text,
                height=350,
                disabled=True,
            )

        # ---------------- Module 4 ----------------

        st.subheader(f"Extracted Skills - {uploaded_file.name}")

        try:
            detected_skills = extract_skills(cleaned_text)
        except Exception as e:
            st.error(e)
            continue

        if detected_skills:
            for skill in detected_skills:
                st.success(skill)
        else:
            st.warning("No technical skills detected.")

        # ---------------- Module 5 ----------------

        score, matched_skills, missing_skills = calculate_match_score(
            detected_skills,
            job_description,
        )

        st.subheader(f"Resume Match Score - {uploaded_file.name}")

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

        # Candidate list for Module 6
        candidates.append(
            {
                "name": uploaded_file.name,
                "score": score,
            }
        )
             # ---------------- Module 6 ----------------

    if candidates:

        st.subheader("🏆 Candidate Ranking")

        try:
            ranked_candidates = rank_candidates(candidates)
        except Exception as e:
            st.error(e)
            return

        ranking_df = pd.DataFrame(ranked_candidates)

        ranking_df = ranking_df.rename(
            columns={
                "rank": "Rank",
                "name": "Resume Name",
                "score": "Score",
            }
        )

        st.dataframe(
            ranking_df,
            use_container_width=True,
            hide_index=True,
        )


def main():
    configure_page()
    render_title()
    render_resume_uploader()


if __name__ == "__main__":
    main()
    
    
