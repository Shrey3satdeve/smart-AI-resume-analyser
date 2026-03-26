"""
utils/parser.py

Hybrid resume parser combining:
  - Regex (email, phone)
  - spaCy NER (name, organizations)
  - Section-based parsing (education, experience)
  - Dynamic skill extraction (via skill_extractor.py)
"""

import re
import spacy  # type: ignore
from typing import Dict, List
from utils.skill_extractor import extract_dynamic_skills  # type: ignore

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# ─── Regex Patterns ──────────────────────────────────────────────────────────
EMAIL_REG = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
PHONE_REG = r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"

def extract_email(text):
    match = re.search(EMAIL_REG, text)
    return match.group(0) if match else None

def extract_phone(text):
    match = re.search(PHONE_REG, text)
    if match:
        phone = match.group(0)
        # Basic cleanup: remove everything except digits and +
        return re.sub(r"[^\d+]", "", phone)
    return None

def extract_name(text):
    """
    Extract name using spaCy NER. 
    Falls back to the first non-empty line if NER fails.
    """
    doc = nlp(text[:1000]) # Scan first 1000 chars for name
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            # Sanity check: must be 2-3 words usually
            name = ent.text.strip()
            if 1 < len(name.split()) < 5:
                return name
    
    # Fallback: First line usually contains the name
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if lines:
        first_line = lines[0]
        if len(first_line.split()) < 5:
            return first_line
            
    return "Unknown Candidate"

def extract_sections(text):
    """
    Split resume into logical sections based on common headers.
    """
    sections: Dict[str, List[str]] = {
        "education": [],
        "experience": [],
        "projects": [],
        "other": []
    }
    
    curr_section = "other"
    lines = text.split("\n")
    
    headers = {
        "education": ["education", "academic", "qualification", "school", "college", "university"],
        "experience": ["experience", "work history", "employment", "professional background", "internship"],
        "projects": ["projects", "personal projects", "academic projects", "key projects"],
        "skills": ["skills", "technical skills", "competencies", "tools", "technologies"]
    }

    for line in lines:
        clean_line = line.strip().lower()
        if not clean_line: continue
        
        # Check if line is a header
        found_header = False
        for sec, keywords in headers.items():
            if any(re.search(rf"^{kw}\b", clean_line) for kw in keywords):
                curr_section = sec
                found_header = True
                break
        
        if not found_header and curr_section in sections:
            sections[curr_section] = sections[curr_section] + [line.strip()]  # type: ignore

    return sections

def parse_resume(text):
    """
    Main entry point for parsing a resume text.
    """
    data = {}
    data["name"] = extract_name(text)
    data["email"] = extract_email(text)
    data["phone"] = extract_phone(text)
    
    # Dynamic skill extraction
    data["skills"] = extract_dynamic_skills(text)
    
    # Section-based extraction
    sections_dict = extract_sections(text)
    data["education"] = [x for i, x in enumerate(set(sections_dict["education"])) if i < 10]
    data["experience"] = [x for i, x in enumerate(set(sections_dict["experience"])) if i < 15]
    
    return data