from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

# Initialize TF-IDF vectorizer
vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')

def embed_chunks(chunks):
    # Fit and transform chunks
    tfidf_matrix = vectorizer.fit_transform(chunks)
    return tfidf_matrix.toarray()

def embed_query(query):
    # Transform query using the fitted vectorizer
    query_vector = vectorizer.transform([query])
    return query_vector.toarray()[0] 