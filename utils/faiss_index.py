def simple_similarity(query_embedding, chunk_embedding):
    """Calculate similarity between query and chunk using word overlap"""
    query_words = set(query_embedding.keys())
    chunk_words = set(chunk_embedding.keys())
    overlap = len(query_words.intersection(chunk_words))
    return overlap

def build_faiss_index(embeddings):
    """Simple index - just return the embeddings"""
    return embeddings

def retrieve_top_k_chunks(index, query_embedding, chunks, k=3):
    """Retrieve top k chunks using simple similarity"""
    similarities = []
    for i, chunk_embedding in enumerate(index):
        similarity = simple_similarity(query_embedding, chunk_embedding)
        similarities.append((similarity, i))
    
    # Sort by similarity (descending) and get top k
    similarities.sort(reverse=True)
    top_indices = [i for _, i in similarities[:k]]
    return [chunks[i] for i in top_indices] 