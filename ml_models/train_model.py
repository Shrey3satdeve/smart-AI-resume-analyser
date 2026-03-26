"""
ml_models/train_model.py

Trains a multiclass SVM classifier using TF-IDF feature extraction.
Uses 'data/resumes.csv' which contains resume text and categories.
Saves model.pkl and vectorizer.pkl for production inference.
"""

import pandas as pd
import pickle
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import classification_report
from config import MODEL_PATH, VECTORIZER_PATH

def clean_text(text):
    """Basic NLP cleaning for model training."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def train_system():
    # ─── Load Data ────────────────────────────────────────────────────────────
    csv_path = "data/resumes.csv"
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found. Cannot train model.")
        return

    print("Loading dataset...")
    df = pd.read_csv(csv_path)
    
    # Dataset expected to have 'Resume_str' or 'Resume' and 'Category'
    # Adjust column names based on common kaggle resume datasets
    if 'Resume_str' in df.columns:
        text_col = 'Resume_str'
    elif 'Resume' in df.columns:
        text_col = 'Resume'
    else:
        print(f"Columns found: {df.columns}. Ensure text column is named 'Resume_str' or 'Resume'")
        return

    print(f"Cleaning {len(df)} samples...")
    X = df[text_col].apply(clean_text)
    y = df["Category"]

    # ─── Feature Extraction ───────────────────────────────────────────────────
    print("Vectorizing text (TF-IDF)...")
    vectorizer = TfidfVectorizer(
        max_features=5000,
        stop_words='english',
        ngram_range=(1, 2)
    )
    X_vectorized = vectorizer.fit_transform(X)

    # ─── Train/Test Split ─────────────────────────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X_vectorized, y, test_size=0.2, random_state=42, stratify=y
    )

    # ─── SVM Training ─────────────────────────────────────────────────────────
    print("Training SVM classifier (this may take a minute)...")
    model = SVC(kernel='linear', C=1.0, probability=True)
    model.fit(X_train, y_train)

    # ─── Evaluation ───────────────────────────────────────────────────────────
    print("Evaluating model...")
    y_pred = model.predict(X_test)
    print("\n" + classification_report(y_test, y_pred))

    # ─── Save Artifacts ───────────────────────────────────────────────────────
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    
    with open(VECTORIZER_PATH, "wb") as f:
        pickle.dump(vectorizer, f)

    print(f"\n✅ Model saved to: {MODEL_PATH}")
    print(f"✅ Vectorizer saved to: {VECTORIZER_PATH}")


if __name__ == "__main__":
    train_system()