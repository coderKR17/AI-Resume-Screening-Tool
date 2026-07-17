# AI-Powered Smart Resume Screening and Candidate Ranking Tool

> IBM AI Internship Project | B.Tech 5th Semester

## 📌 Project Overview

The **AI-Powered Smart Resume Screening and Candidate Ranking Tool** is an
intelligent recruitment-assistance application designed to automate the
process of screening resumes against a given job description (JD). The
tool aims to help recruiters and hiring teams quickly identify the most
suitable candidates by parsing resumes, extracting relevant information,
and ranking candidates based on their similarity/fit to the job
requirements.

This repository currently contains the **project scaffolding only**.
Business logic (resume parsing, NLP-based scoring, and ranking
algorithms) will be implemented in subsequent development phases.

## ✨ Features

Planned features for this project include:

- 📄 Bulk resume upload (PDF/DOCX support)
- 🧹 Automated text extraction and preprocessing of resumes
- 🧠 NLP-based similarity scoring between resumes and job descriptions
- 🏆 Candidate ranking based on relevance/fit score
- 📊 Interactive Streamlit dashboard for recruiters
- 📥 Exportable shortlisting reports
- 🔍 Keyword and skill-gap analysis

*Note: Features listed above represent the project roadmap. No business
logic has been implemented in the current scaffolding stage.*

## 🗂️ Folder Structure

```
ai-resume-screening-tool/
│
├── app.py                     # Streamlit application entry point
├── requirements.txt           # Python dependencies
├── .gitignore                 # Git ignore rules
├── README.md                  # Project documentation
│
├── src/                       # Core application source code
│   ├── __init__.py
│   ├── config/                # App configuration, constants, settings
│   │   └── __init__.py
│   ├── data_processing/       # Resume/JD ingestion & preprocessing
│   │   └── __init__.py
│   ├── models/                # ML/NLP scoring & ranking logic
│   │   └── __init__.py
│   ├── utils/                 # Shared/reusable helper functions
│   │   └── __init__.py
│   └── ui/                    # Streamlit UI components & layouts
│       └── __init__.py
│
├── data/                      # Data storage (not committed to Git)
│   ├── raw/                   # Uploaded/raw resumes and JDs
│   └── processed/             # Cleaned/preprocessed data
│
├── models/                    # Saved/serialized ML model artifacts
│
├── assets/                    # Static assets (images, logos, icons, CSS)
│
├── outputs/                   # Generated reports & ranked candidate lists
│
└── docs/                      # Additional project documentation
```

## ⚙️ Installation

### Prerequisites

- Python **3.11+**
- pip (Python package manager)
- (Recommended) A virtual environment tool such as `venv`

### Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-resume-screening-tool
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## ▶️ How to Run

Once dependencies are installed, launch the Streamlit application with:

```bash
streamlit run app.py
```

The app will start a local development server and open automatically in
your default web browser (typically at `http://localhost:8501`).

## 🚀 Future Improvements

- Implement resume parsing for PDF and DOCX formats
- Integrate NLP models (e.g., spaCy, sentence embeddings) for semantic
  similarity scoring between resumes and job descriptions
- Build a candidate ranking algorithm with configurable weighting
- Add a recruiter dashboard with filtering and sorting capabilities
- Support exporting shortlisted candidates as CSV/PDF reports
- Add authentication for recruiter accounts
- Integrate with an Applicant Tracking System (ATS) via API
- Add unit tests and CI/CD pipeline
- Deploy the application on cloud platforms (e.g., IBM Cloud, Streamlit
  Community Cloud)

## 🛠️ Tech Stack

| Layer      | Technology       |
|------------|------------------|
| Frontend   | Streamlit        |
| Backend    | Python           |
| Language   | Python 3.11+     |

## 📄 License

This project is developed for academic and internship purposes as part
of the IBM AI Internship program.
