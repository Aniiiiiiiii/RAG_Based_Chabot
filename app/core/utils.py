import hashlib
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')

def hash_question(question):
    """Hashes the question using SHA256."""
    return hashlib.sha256(question.encode()).hexdigest()

def extract_keywords(question):
    """Extracts keywords from the question."""
    words = word_tokenize(question)
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word.lower() not in stop_words]
    pos_tags = pos_tag(filtered_words)
    keywords = [word for word, pos in pos_tags if pos.startswith('NN') or pos.startswith('VB') or pos.startswith('JJ')]
    return keywords