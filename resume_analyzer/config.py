"""
config.py – Central configuration for the Resume Analyzer application.
All paths, limits, and settings are defined here for easy modification.
"""

import os

# ─── Base Paths ──────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── Upload Settings ─────────────────────────────────────────────────────────
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
ALLOWED_EXTENSIONS = {"pdf", "docx"}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB per file

# ─── Database ────────────────────────────────────────────────────────────────
DB_PATH = os.path.join(BASE_DIR, "database", "resume.db")

# ─── ML Model Paths ──────────────────────────────────────────────────────────
MODEL_PATH      = os.path.join(BASE_DIR, "ml_models", "model.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "ml_models", "vectorizer.pkl")
LABEL_ENCODER_PATH = os.path.join(BASE_DIR, "ml_models", "label_encoder.pkl")

# ─── Flask Settings ──────────────────────────────────────────────────────────
SECRET_KEY = "resume_analyzer_secret_key_2024"
DEBUG = True

# ─── ATS Scoring Weights ─────────────────────────────────────────────────────
SCORE_WEIGHTS = {
    "skills":      30,   # richness of extracted skills
    "experience":  25,   # has relevant experience keywords
    "education":   20,   # education section detected
    "contact":     15,   # email + phone present
    "keywords":    10,   # keyword density in resume
}
