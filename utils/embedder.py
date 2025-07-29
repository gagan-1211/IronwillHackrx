import re
from collections import Counter
import numpy as np
from sentence_transformers import SentenceTransformer
import logging

# Initialize logger
logger = logging.getLogger(__name__)

# Use a lightweight model that works well on Vercel
MODEL_NAME = "all-MiniLM-L6-v2"  # Small, fast, good performance
model = None

def get_model():
    """Lazy load the model to avoid memory issues on Vercel"""
    global model
    if model is None:
        try:
            model = SentenceTransformer(MODEL_NAME)
            logger.info(f"Loaded sentence transformer model: {MODEL_NAME}")
        except Exception as e:
            logger.error(f"Failed to load sentence transformer: {e}")
            # Fallback to simple embedding
            return None
    return model

def simple_embed(text):
    """Simple word frequency embedding as fallback"""
    words = re.findall(r'\b\w+\b', text.lower())
    word_freq = Counter(words)
    return word_freq

def embed_text(text):
    """Embed text using sentence transformers or fallback to simple embedding"""
    try:
        model = get_model()
        if model:
            # Clean and truncate text for better embedding
            cleaned_text = re.sub(r'\s+', ' ', text.strip())
            if len(cleaned_text) > 512:  # Truncate for model efficiency
                cleaned_text = cleaned_text[:512]
            embedding = model.encode(cleaned_text)
            return embedding.tolist()
        else:
            # Fallback to simple embedding
            return simple_embed(text)
    except Exception as e:
        logger.warning(f"Embedding failed, using fallback: {e}")
        return simple_embed(text)

def embed_chunks(chunks):
    """Create embeddings for chunks"""
    embeddings = []
    for i, chunk in enumerate(chunks):
        try:
            embedding = embed_text(chunk)
            embeddings.append(embedding)
            if i % 10 == 0:  # Log progress every 10 chunks
                logger.info(f"Embedded {i+1}/{len(chunks)} chunks")
        except Exception as e:
            logger.error(f"Failed to embed chunk {i}: {e}")
            # Add zero embedding as fallback
            embeddings.append([0.0] * 384 if isinstance(embed_text("test"), list) else {})
    return embeddings

def embed_query(query):
    """Create embedding for query"""
    return embed_text(query)

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors"""
    try:
        if isinstance(vec1, dict) and isinstance(vec2, dict):
            # Simple word overlap for dict embeddings
            words1 = set(vec1.keys())
            words2 = set(vec2.keys())
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            return intersection / union if union > 0 else 0
        else:
            # Cosine similarity for vector embeddings
            vec1 = np.array(vec1)
            vec2 = np.array(vec2)
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            return dot_product / (norm1 * norm2) if norm1 * norm2 > 0 else 0
    except Exception as e:
        logger.error(f"Similarity calculation failed: {e}")
        return 0.0 