import re


def calculate_match_score(resume_skills, job_description):
    """
    Compare resume skills with job description and calculate match score.
    """

    if not resume_skills or not job_description.strip():
        return 0, [], []

    job_description = job_description.lower()

    matched = []

    for skill in resume_skills:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"

        if re.search(pattern, job_description):
            matched.append(skill)

    missing = list(set(resume_skills) - set(matched))

    score = int((len(matched) / len(resume_skills)) * 100)

    return score, matched, missing