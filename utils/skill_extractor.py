"""
utils/skill_extractor.py

Fully DYNAMIC skill extraction — NO predefined CSV or static lists.
Uses spaCy NLP:
  - Noun phrase chunking (bigrams/trigrams)
  - Named Entity filtering (removes PERSON, GPE, DATE, etc.)
  - POS tagging (PROPN for single tech terms)
  - Frequency-based relevance filtering
  - Context-aware blacklist pruning
"""

import sys
import os
import re

# Ensure project root is in path for imports to work across different IDE setups
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import spacy  # type: ignore
from collections import Counter

# Load spaCy model once at module level
nlp = spacy.load("en_core_web_sm")
STOP_WORDS = nlp.Defaults.stop_words

# ─── Noise blacklist (domain-agnostic common words) ───────────────────────────
BLACKLIST = {
    "experience", "experiences", "year", "years", "month", "months",
    "project", "projects", "work", "working", "worker", "team", "teams",
    "role", "roles", "responsibility", "responsibilities", "company",
    "organization", "detail", "details", "resume", "curriculum", "vitae",
    "candidate", "applicant", "employer", "employee", "position", "job",
    "ability", "abilities", "skill", "skills", "knowledge", "understanding",
    "background", "summary", "objective", "profile", "reference", "date",
    "address", "city", "state", "country", "email", "phone", "mobile",
    "proficiency", "proficient", "communication", "management", "development",
    "time", "use", "result", "results", "list", "area", "areas",
    "good", "great", "strong", "excellent", "various", "different",
    "include", "includes", "including", "related", "relevant", "etc",
    "etc.", "e.g", "i.e", "page", "section", "professional", "education",
    "higher", "secondary", "university", "college", "school", "b.tech",
    "bachelor", "master", "degree", "cgpa", "percentage", "academy",
    "institute", "department", "board", "completion", "certification",
    "certifications", "certified", "focus", "solution", "solutions",
    "accuracy", "consistency", "pipeline", "pipelines", "workflow", "workflows",
    "entry", "system", "systems", "architecture", "architectures", "model", 
    "models", "dataset", "datasets", "deployment", "deployments", "reporting",
    "schema"
}

def _is_valid_skill(token_text: str) -> bool:
    """Return True if the term is a valid candidate skill."""
    text = token_text.strip(".,;:?!()[]{}'\" \t|-").lower()
    
    # Must be at least 2 chars (except C, R)
    if len(text) < 2 and text not in ('c', 'r'):
        return False
        
    # Block emails and URLs
    if '@' in text or 'http' in text or 'www' in text:
        return False
        
    # Block phone numbers and pure digits (3+ consecutive digits)
    if re.search(r'\d{3,}', text):
        return False
        
    if text in BLACKLIST or text in STOP_WORDS:
        return False
        
    # Check if the entire phrase is composed entirely of stopwords
    words = text.split()
    if all(w in STOP_WORDS or w in BLACKLIST for w in words):
        return False
        
    # Filter pure numeric or special-char tokens
    stripped = text.replace("-", "").replace("+", "").replace("#", "").replace(".", "").replace(",", "")
    if stripped.isdigit():
        return False
        
    return True


def extract_dynamic_skills(text: str) -> list[str]:
    """
    Extract skills dynamically from resume text using NLP.
    """
    doc = nlp(text)
    candidates = []

    # 1. Identify forbidden tokens from specific Named Entities
    forbidden_tokens = set()
    forbidden_labels = {"DATE", "TIME", "PERCENT", "MONEY", "QUANTITY", "ORDINAL", "CARDINAL", "LOC", "GPE", "FAC", "PERSON", "LANGUAGE"}
    for ent in doc.ents:
        if ent.label_ in forbidden_labels:
            for i in range(ent.start, ent.end):
                forbidden_tokens.add(i)

    # Also block tokens that are heavily numeric or url/emails
    for token in doc:
        if token.like_email or token.like_url or token.like_num:
            forbidden_tokens.add(token.i)

    # ── Step 1: Noun chunks (2–3 words → multi-word skills) ──────────────────
    for chunk in doc.noun_chunks:
        # Skip chunk if it contains any forbidden entity token
        if any(token.i in forbidden_tokens for token in chunk):
            continue
            
        phrase = chunk.text.strip(".,;:?!()[]{}'\" \t|-").lower()
        words = phrase.split()
        
        # Limit to 2-3 words (4 is usually a sentence fragment like 'professional summary machine learning')
        if 2 <= len(words) <= 3:
            # remove leading/trailing stop words (like 'strong', 'and', 'with')
            while words and (words[0] in STOP_WORDS or words[0] in BLACKLIST):
                words.pop(0)
            while words and (words[-1] in STOP_WORDS or words[-1] in BLACKLIST):
                words.pop()
            
            phrase = " ".join(words)
            if _is_valid_skill(phrase):
                candidates.append(phrase)

    # ── Step 2: Single-token Proper Nouns and Nouns ──────────────────────────
    for token in doc:
        # Skip forbidden
        if token.i in forbidden_tokens:
            continue
            
        word = token.lemma_.lower().strip(".,;:?!()[]{}'\" \t|-")
        # Keep Proper Nouns (PROPN) or Nouns (NOUN) that pass validation
        if token.pos_ in ("PROPN", "NOUN") and not token.is_stop:
            if _is_valid_skill(word):
                candidates.append(word)

    # ── Step 3: Frequency-based relevance ────────────────────────────────────
    freq = Counter(candidates)
    
    filtered = []
    for term, count in freq.items():
        words = term.split()
        if len(words) >= 2:
            filtered.append(term)
        elif count >= 2 or len(term) >= 3 or term in ('c', 'r', 'go'):
            filtered.append(term)

    # ── Step 4: Final dedup and sort ─────────────────────────────────────────
    seen = set()
    result: list[str] = []
    for skill in sorted(filtered, key=len, reverse=True):
        # avoid sub-phrases perfectly matching inside already-included longer phrases
        # e.g., don't add "sql" if "mysql" is there? Wait, "sql" in "mysql" -> False via \b regex. Good.
        # e.g., don't add "machine learning" if "advanced machine learning" is there -> True via \b regex. Good.
        is_subphrase = False
        escaped_skill = re.escape(skill)
        for longer in seen:
            if re.search(r'\b' + escaped_skill + r'\b', longer):
                is_subphrase = True
                break
                
        if not is_subphrase:
            seen.add(skill)
            result.append(str(skill))

    return list(result)[:50]  # type: ignore