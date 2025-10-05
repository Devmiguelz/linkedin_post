# utils/text_utils.py
import re
from collections import Counter

def normalize_text(s: str):
    if not s:
        return ""
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def extract_common_words(texts, top_n=20, stopwords=None):
    tokens = []
    for t in texts:
        t = re.sub(r'[^\w\s]', ' ', t.lower())
        tokens += t.split()
    if not stopwords:
        stopwords = set(["de","la","el","y","en","a","con","que","para","los","las","un","una","mi","me","se","es","al"])
    filtered = [w for w in tokens if w not in stopwords and len(w)>2]
    c = Counter(filtered)
    return c.most_common(top_n)
