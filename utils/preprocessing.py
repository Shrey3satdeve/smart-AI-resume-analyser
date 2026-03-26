import re
import nltk
import spacy
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download NLTK resources (run once)
nltk.download('punkt')
nltk.download('stopwords')

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

stop_words = set(stopwords.words('english'))


def clean_text(text):
    """
    Step 1: Basic cleaning using regex
    """
    text = re.sub(r'\n', ' ', text)           # remove newlines
    text = re.sub(r'\s+', ' ', text)          # remove extra spaces
    text = re.sub(r'[^a-zA-Z0-9@.+# ]', '', text)  # keep important chars
    return text


def preprocess_text(text):
    """
    Full NLP pipeline:
    cleaning → tokenization → stopword removal → lemmatization
    """

    # 1. Clean text
    text = clean_text(text)

    # 2. Lowercase
    text = text.lower()

    # 3. Tokenization
    tokens = word_tokenize(text)

    # 4. Remove stopwords
    tokens = [word for word in tokens if word not in stop_words]

    # 5. Lemmatization using spaCy
    doc = nlp(" ".join(tokens))
    lemmas = [token.lemma_ for token in doc]

    return lemmas


def get_pos_tags(text):
    """
    POS tagging (from paper concepts)
    """
    doc = nlp(text)
    return [(token.text, token.pos_) for token in doc]


def get_named_entities(text):
    """
    Named Entity Recognition (NER)
    Extract name, org, location etc.
    """
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return entities