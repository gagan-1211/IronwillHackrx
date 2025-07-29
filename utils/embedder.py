import re
from collections import Counter

def simple_embed(text):
    """Simple word frequency embedding"""
    words = re.findall(r'\b\w+\b', text.lower())
    word_freq = Counter(words)
    return word_freq

def embed_chunks(chunks):
    """Create simple embeddings for chunks"""
    embeddings = []
    for chunk in chunks:
        embedding = simple_embed(chunk)
        embeddings.append(embedding)
    return embeddings

def embed_query(query):
    """Create simple embedding for query"""
    return simple_embed(query) 