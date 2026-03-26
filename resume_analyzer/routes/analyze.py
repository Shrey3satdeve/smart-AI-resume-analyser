"""
routes/analyze.py

Flask Blueprint for the analysis pipeline.
Processes uploaded resumes, runs NLP & ML steps, and saves to DB.
"""

import os
import uuid
from flask import Blueprint, request, jsonify, render_template, current_app, session
from werkzeug.utils import secure_filename

from utils.text_extraction import extract_text
from utils.parser import parse_resume
from utils.scoring import compute_ats_score
from utils.job_matcher import compute_job_match
from utils.recommender import generate_recommendations
from ml_models.evaluator import predict_category
from database.db import insert_candidate, get_candidate_by_id

analyze_bp = Blueprint("analyze", __name__)

def run_analysis_pipeline(file_path, job_desc, session_id):
    """
    Executes the full end-to-end analysis for a single resume file.
    """
    # 1. Extract Text
    raw_text = extract_text(file_path)
    if not raw_text.strip():
        return None

    # 2. Parse Structured Data
    parsed_data = parse_resume(raw_text)
    
    # 3. ML Category Prediction
    prediction = predict_category(raw_text)
    
    # 4. ATS Scoring
    score_data = compute_ats_score(parsed_data, raw_text)
    
    # 5. Job Matching (Semantic)
    match_data = compute_job_match(raw_text, job_desc)
    
    # 6. Recommendations
    recommendations = generate_recommendations(
        parsed_data,
        score_data["breakdown"],
        match_data["missing_skills"],
        prediction,
        match_data["match_score"]
    )

    # 7. Merge & Save to DB
    final_data = {
        "name": parsed_data["name"],
        "email": parsed_data["email"],
        "phone": parsed_data["phone"],
        "skills": parsed_data["skills"],
        "education": parsed_data["education"],
        "experience": parsed_data["experience"],
        "ats_score": score_data["total"],
        "prediction": prediction,
        "match_score": match_data["match_score"],
        "missing_skills": match_data["missing_skills"],
        "recommendations": recommendations,
        "job_description": job_desc,
        "filename": os.path.basename(file_path),
        "session_id": session_id
    }
    
    candidate_id = insert_candidate(final_data)
    final_data["id"] = candidate_id
    
    return final_data

@analyze_bp.route("/analyze/<int:candidate_id>")
def view_result(candidate_id):
    """
    View analysis result for a specific candidate.
    """
    candidate = get_candidate_by_id(candidate_id)
    if not candidate:
        return "Not Found", 404
        
    return render_template("result.html", candidate=candidate)
