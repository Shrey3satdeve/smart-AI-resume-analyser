"""
database/db.py

SQLite database management for candidate storage and ranking.
Extended with columns for match score, missing skills, recommendations,
and metadata for ranking multiple resumes.
"""

import sqlite3
import json
import os
from config import DB_PATH

def get_connection():
    """Establish connection to SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn


def create_tables():
    """Initialize database tables."""
    conn = get_connection()
    cursor = conn.cursor()

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        phone TEXT,
        skills TEXT,          -- JSON string
        education TEXT,       -- JSON string
        experience TEXT,      -- JSON string
        ats_score REAL,
        prediction TEXT,      -- Category prediction
        match_score REAL,     -- Similarity to job description
        missing_skills TEXT,  -- JSON string
        recommendations TEXT, -- JSON string
        job_description TEXT, -- Reference JD
        filename TEXT,
        session_id TEXT       -- For grouping batch uploads
    )
    """)

    conn.commit()
    conn.close()


def insert_candidate(data: dict):
    """
    Insert analyzed candidate data into DB.
    Data values for lists are automatically serialized to JSON.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO candidates (
        name, email, phone, skills, education, experience, ats_score, 
        prediction, match_score, missing_skills, recommendations, 
        job_description, filename, session_id
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("name"),
        data.get("email"),
        data.get("phone"),
        json.dumps(data.get("skills", [])),
        json.dumps(data.get("education", [])),
        json.dumps(data.get("experience", [])),
        data.get("ats_score", 0.0),
        data.get("prediction", "Other"),
        data.get("match_score", 0.0),
        json.dumps(data.get("missing_skills", [])),
        json.dumps(data.get("recommendations", [])),
        data.get("job_description", ""),
        data.get("filename", ""),
        data.get("session_id", "")
    ))

    last_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return last_id


def get_all_candidates():
    """Fetch all candidates sorted by ATS score descending."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates ORDER BY ats_score DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_session_candidates(session_id: str):
    """Fetch candidates for a specific upload session sorted by match_score."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM candidates WHERE session_id = ? ORDER BY match_score DESC, ats_score DESC", 
        (session_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_candidate_by_id(candidate_id: int):
    """Fetch a single candidate by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates WHERE id = ?", (candidate_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def delete_candidate(candidate_id: int):
    """Remove a candidate from DB."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM candidates WHERE id = ?", (candidate_id,))
    conn.commit()
    conn.close()