"""
utils/job_matcher.py

Semantic job-resume matching using TF-IDF + cosine similarity.
Also performs dynamic missing-skills detection by comparing
extracted resume skills against job description terms.
"""

import re
import sys
import os

# Ensure project root is in path for imports to work across different IDE setups
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore
from sklearn.metrics.pairwise import cosine_similarity  # type: ignore
from utils.skill_extractor import extract_dynamic_skills, BLACKLIST, STOP_WORDS  # type: ignore


def _round_2(val: float) -> float:
    """Helper to round to 2 decimal places, avoiding IDE overload issues."""
    try:
        return float(f"{val:.2f}")
    except (ValueError, TypeError):
        return 0.0

def _clean(text: str) -> str:
    """Light cleaning for matching purposes."""
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^a-zA-Z0-9+#.\s]", " ", text)
    return text.lower().strip()

def compute_job_match(resume_text: str, job_description: str) -> dict:
    """
    Compute semantic similarity between a resume and a job description.

    Uses TF-IDF vectorizer + cosine similarity to get match percentage.
    Also identifies skills mentioned in JD that are absent from resume.

    Args:
        resume_text:     Raw text extracted from the resume.
        job_description: Raw job description text.

    Returns:
        {
          "match_score":     <float 0.0–100.0>,
          "missing_skills":  [list of missing skill strings],
          "jd_skills":       [skills extracted from JD],
          "resume_skills":   [skills extracted from resume],
        }
    """
    if not job_description or not job_description.strip():
        return {
            "match_score": 0.0,
            "missing_skills": [],
            "jd_skills": [],
            "resume_skills": [],
        }

    clean_resume = _clean(resume_text)
    clean_jd     = _clean(job_description)

    # ── TF-IDF cosine similarity ──────────────────────────────────────────────
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        stop_words="english",
        max_features=10000,
    )
    try:
        tfidf_matrix = vectorizer.fit_transform([clean_resume, clean_jd])
        similarity   = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        # Force float to avoid numpy scalar typing issues with round overload
        match_score  = _round_2(float(similarity[0][0]) * 100)
    except Exception:
        match_score = 0.0
    # ── Dynamic skill extraction from both sides ──────────────────────────────
    resume_skills = set(extract_dynamic_skills(resume_text))
    jd_skills     = set(extract_dynamic_skills(job_description))

    # Also pull important single words from JD (tech terms etc.)
    jd_words = {
        w.lower() for w in re.findall(r"\b[a-zA-Z][a-zA-Z0-9+#.\-]{1,25}\b", job_description)
        if w.lower() not in BLACKLIST and w.lower() not in STOP_WORDS and len(w) > 2
    }
    jd_skills.update(jd_words)

    # Missing = skills in JD not in resume (set difference)
    missing_skills = list(jd_skills - resume_skills)

    # Filter noise from missing list
    missing_filtered = [
        str(s) for s in missing_skills
        if s not in BLACKLIST and len(s) > 2 and not s.isdigit()
    ]
    # Slice as an explicit list
    final_missing = list(missing_filtered)[:30]  # type: ignore

    return {
        "match_score":    match_score,
        "missing_skills": final_missing,
        "jd_skills":      list(sorted(jd_skills))[:40],  # type: ignore
        "resume_skills":  list(sorted(resume_skills)),
    }
