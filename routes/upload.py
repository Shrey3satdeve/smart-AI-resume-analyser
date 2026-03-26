"""
routes/upload.py

Handles batch file uploads and job description matching.
Manages file storage and initiates the analysis pipeline.
"""

import os
import uuid
from flask import Blueprint, request, redirect, url_for, render_template, current_app, session, flash  # type: ignore
from werkzeug.utils import secure_filename  # type: ignore
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS  # type: ignore
from routes.analyze import run_analysis_pipeline  # type: ignore

upload_bp = Blueprint("upload", __name__)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # 1. Get Job Description
        job_desc = request.form.get("job_description", "")
        
        # 2. Get Files
        files = request.files.getlist("resumes")
        if not files or files[0].filename == "":
            flash("No files selected!")
            return redirect(request.url)

        # 3. Create Session ID for batch
        session_id = str(uuid.uuid4())
        session["last_session_id"] = session_id
        
        num_processed = 0
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Ensure unique filename
                unique_filename = f"{uuid.uuid4()}_{filename}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                file.save(file_path)
                
                result = run_analysis_pipeline(file_path, job_desc, session_id)
                if result:
                    num_processed = num_processed + 1  # type: ignore

        if num_processed > 0:
            flash(f"Successfully analyzed {num_processed} resumes!")
            return redirect(url_for("upload.ranking"))
        else:
            flash("Failed to analyze any resumes. Check file formats.")
            return redirect(request.url)

    return render_template("upload.html")

@upload_bp.route("/ranking")
def ranking():
    """
    Displays the analysis results for the most recent upload batch,
    ranked by job match and ATS score.
    """
    from database.db import get_session_candidates  # type: ignore
    session_id = session.get("last_session_id")
    if not session_id:
        return redirect(url_for("dashboard.view_dashboard"))
        
    candidates = get_session_candidates(session_id)
    return render_template("ranking.html", candidates=candidates)
