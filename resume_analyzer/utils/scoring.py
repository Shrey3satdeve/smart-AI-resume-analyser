"""
utils/scoring.py

ATS (Applicant Tracking System) weighted scoring engine.
Scores a resume 0–100 based on:
  - Skills richness  (30 pts)
  - Experience       (25 pts)
  - Education        (20 pts)
  - Contact info     (15 pts)
  - Keyword density  (10 pts)

Returns both the total score and a per-category breakdown.
"""

import re
import sys
import os

import importlib

# Default fallback weights if file not found locally
SCORE_WEIGHTS = {
    "skills": 30, "experience": 25, "education": 20, "contact": 15, "keywords": 10
}

try:
    # Use dynamic import to satisfy static linter when root is not in path
    config = importlib.import_module("config")
    SCORE_WEIGHTS = getattr(config, "SCORE_WEIGHTS", SCORE_WEIGHTS)
except (ImportError, ModuleNotFoundError):
    pass

def _round_2(val: float) -> float:
    """Helper to round to 2 decimal places, avoiding IDE overload issues."""
    try:
        return float(f"{val:.2f}")
    except (ValueError, TypeError):
        return 0.0

# ─── Keyword banks ────────────────────────────────────────────────────────────
EXPERIENCE_KEYWORDS = {
    "experience", "intern", "internship", "worked", "developer", "engineer",
    "analyst", "manager", "led", "managed", "developed", "designed",
    "implemented", "built", "created", "deployed", "architected", "operated",
    "maintained", "collaborated", "contributed", "achieved", "delivered",
}

EDUCATION_KEYWORDS = {
    "b.tech", "m.tech", "bachelor", "master", "mba", "bsc", "msc",
    "phd", "diploma", "degree", "university", "college", "institute",
    "engineering", "science", "technology", "graduation", "b.e", "m.e",
    "b.s", "m.s", "b.a", "m.a", "postgraduate", "undergraduate",
}

STRONG_KEYWORDS = {
    "python", "java", "sql", "machine learning", "deep learning", "nlp",
    "data science", "flask", "django", "react", "node", "aws", "docker",
    "kubernetes", "git", "api", "database", "algorithm", "neural network",
    "tensorflow", "pytorch", "scikit", "pandas", "numpy", "javascript",
    "typescript", "linux", "agile", "scrum", "devops", "cloud",
}


def _score_skills(skills: list) -> float:
    """Score based on number and quality of extracted skills."""
    count = len(skills)
    if count == 0:
        return 0.0
    elif count <= 5:
        return _round_2(SCORE_WEIGHTS["skills"] * 0.3)
    elif count <= 10:
        return _round_2(SCORE_WEIGHTS["skills"] * 0.55)
    elif count <= 20:
        return _round_2(SCORE_WEIGHTS["skills"] * 0.75)
    elif count <= 35:
        return _round_2(SCORE_WEIGHTS["skills"] * 0.90)
    else:
        return float(SCORE_WEIGHTS["skills"])


def _score_experience(text: str) -> float:
    """Score based on experience-related keywords found."""
    text_lower = text.lower()
    hits = sum(1 for kw in EXPERIENCE_KEYWORDS if kw in text_lower)
    ratio = min(hits / len(EXPERIENCE_KEYWORDS), 1.0)
    raw = SCORE_WEIGHTS["experience"] * ratio
    # Bonus: detect years of experience mention
    if re.search(r"\d+\+?\s*years?\s+of\s+experience", text_lower):
        raw = min(raw * 1.2, SCORE_WEIGHTS["experience"])
    return _round_2(raw)


def _score_education(text: str) -> float:
    """Score based on education keywords detected."""
    text_lower = text.lower()
    hits = sum(1 for kw in EDUCATION_KEYWORDS if kw in text_lower)
    if hits == 0:
        return 0.0
    elif hits == 1:
        return _round_2(SCORE_WEIGHTS["education"] * 0.5)
    elif hits <= 3:
        return _round_2(SCORE_WEIGHTS["education"] * 0.75)
    else:
        return float(SCORE_WEIGHTS["education"])


def _score_contact(email: str | None, phone: str | None) -> float:
    """Score based on presence of email and phone."""
    w = SCORE_WEIGHTS["contact"]
    if email and phone:
        return float(w)
    elif email or phone:
        return _round_2(w * 0.5)
    return 0.0


def _score_keywords(text: str) -> float:
    """Score based on density of strong industry keywords."""
    text_lower = text.lower()
    hits = sum(1 for kw in STRONG_KEYWORDS if kw in text_lower)
    ratio = min(hits / 15, 1.0)  # max out at 15 hits
    return _round_2(SCORE_WEIGHTS["keywords"] * ratio)


def compute_ats_score(parsed_data: dict, raw_text: str) -> dict:
    """
    Compute ATS score for a resume.

    Args:
        parsed_data: Result dict from parse_resume()
        raw_text:    Raw resume text string

    Returns:
        {
          "total":      <float 0–100>,
          "breakdown":  { skills, experience, education, contact, keywords }
        }
    """
    skills     = parsed_data.get("skills", [])
    email      = parsed_data.get("email")
    phone      = parsed_data.get("phone")

    breakdown = {
        "skills":     _score_skills(skills),
        "experience": _score_experience(raw_text),
        "education":  _score_education(raw_text),
        "contact":    _score_contact(email, phone),
        "keywords":   _score_keywords(raw_text),
    }

    # Sum up all scores and round to 2 decimal places
    raw_total = float(sum(breakdown.values()))
    # Use string formatting to avoid IDE round() overload issues
    total = _round_2(raw_total)
    total = min(total, 100.0)  # cap at 100

    return {"total": total, "breakdown": breakdown}
