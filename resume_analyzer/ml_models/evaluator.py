"""
ml_models/evaluator.py

Predicts the category of a resume using the trained SVM model.
If the model is not found, provides a fallback classification based on keywords.
"""

import os
import pickle
import re
from config import MODEL_PATH, VECTORIZER_PATH  # type: ignore

# ─── Fallback category keywords (if model not trained) ────────────────────────
CATEGORY_KEYWORDS = {
    "Data Science": ["data science", "machine learning", "deep learning", "nlp", "python", "pandas", "pytorch", "tensorflow"],
    "Web Development": ["web development", "frontend", "backend", "fullstack", "react", "angular", "node", "javascript", "html", "css", "django", "flask"],
    "Java Developer": ["java", "spring boot", "hibernate", "microservices", "j2ee"],
    "Android Developer": ["android", "kotlin", "mobile app", "xml", "retro-fit"],
    "Python Developer": ["python", "automation", "scripting", "scraping", "api"],
    "DevOps Engineer": ["devops", "aws", "docker", "kubernetes", "jenkins", "terraform", "ci/cd", "cloud"],
    "Database Administrator": ["database", "sql", "postgresql", "mysql", "mongodb", "oracle", "dba", "tuning"],
    "HR": ["hr", "human resources", "recruitment", "hiring", "payroll", "onboarding"],
    "Advocate": ["advocate", "law", "legal", "court", "litigation", "criminal", "civil"],
    "Mechanical Engineer": ["mechanical", "cad", "solidworks", "maintenance", "manufacturing", "autocad"],
    "Health and Fitness": ["health", "fitness", "gym", "nutrition", "trainer", "yoga", "wellness"],
    "Business Development": ["business development", "sales", "revenue", "lead generation", "marketing"],
}


def _heuristic_predict(text: str) -> str:
    """Fallback rule-based classification."""
    text_lower = text.lower()
    scores = {}
    for cat, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[cat] = score
    
    if not scores:
        return "Other"
    
    return max(scores.keys(), key=lambda k: scores[k])


def predict_category(text: str) -> str:
    """
    Predict resume category.
    
    Tries to use SVM model first. Falls back to keyword matching if 
    model files are missing.
    """
    if not os.path.exists(MODEL_PATH) or not os.path.exists(VECTORIZER_PATH):
        print("Warning: Model or Vectorizer file not found. Using heuristic fallback.")
        return _heuristic_predict(text)

    try:
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        with open(VECTORIZER_PATH, "rb") as f:
            vectorizer = pickle.load(f)

        # Basic cleaning for model
        clean_text = re.sub(r'[^a-zA-Z\s]', ' ', text.lower())
        X_vec = vectorizer.transform([clean_text])
        prediction = model.predict(X_vec)
        
        return str(prediction[0])
    except Exception as e:
        print(f"Error during ML prediction: {e}")
        return _heuristic_predict(text)
