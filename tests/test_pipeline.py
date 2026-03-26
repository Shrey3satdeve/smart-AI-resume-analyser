"""
tests/test_pipeline.py

Manual test script to verify that all core NLP and ML modules 
are working correctly after training.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.parser import parse_resume
from utils.scoring import compute_ats_score
from utils.job_matcher import compute_job_match
from ml_models.evaluator import predict_category

SAMPLE_RESUME = """
John Doe
Email: john.doe@example.com
Phone: +1 123 456 7890

EXPERIENCE
Python Developer at TechCorp
- Developed web applications using Flask and Django.
- Managed SQL databases and optimized queries.
- Implemented CI/CD pipelines with Docker and Jenkins.

EDUCATION
B.Tech in Computer Science
University of Excellence, 2020

SKILLS
Python, Flask, Django, SQL, Docker, Kubernetes, Git, Machine Learning.
"""

SAMPLE_JD = """
We are looking for a Senior Python Developer with 5+ years of experience.
Must be proficient in Flask, Django, and PostgreSQL.
Experience with AWS, Terraform, and Microservices is a plus.
"""

def run_test():
    print("--- 1. Testing Parser ---")
    parsed = parse_resume(SAMPLE_RESUME)
    print(f"Name: {parsed['name']}")
    print(f"Email: {parsed['email']}")
    print(f"Phone: {parsed['phone']}")
    print(f"Skills Found: {len(parsed['skills'])} skills")

    print("\n--- 2. Testing ML Category ---")
    category = predict_category(SAMPLE_RESUME)
    print(f"Predicted Category: {category}")

    print("\n--- 3. Testing ATS Scoring ---")
    score_data = compute_ats_score(parsed, SAMPLE_RESUME)
    print(f"Total Score: {score_data['total']}")

    print("\n--- 4. Testing Job Match ---")
    match_data = compute_job_match(SAMPLE_RESUME, SAMPLE_JD)
    print(f"Match Score: {match_data['match_score']}%")
    print(f"Missing Skills: {match_data['missing_skills']}")

    print("\n✅ Pipeline Test Complete!")

if __name__ == "__main__":
    run_test()
