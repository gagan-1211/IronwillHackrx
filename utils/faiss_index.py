from utils.embedder import cosine_similarity
import logging

logger = logging.getLogger(__name__)

def build_faiss_index(embeddings):
    """Build simple index - just return the embeddings"""
    logger.info(f"Built index with {len(embeddings)} embeddings")
    return embeddings

def retrieve_top_k_chunks(index, query_embedding, chunks, k=5):
    """Retrieve top k chunks using cosine similarity"""
    try:
        similarities = []
        for i, chunk_embedding in enumerate(index):
            try:
                similarity = cosine_similarity(query_embedding, chunk_embedding)
                similarities.append((similarity, i))
            except Exception as e:
                logger.warning(f"Failed to calculate similarity for chunk {i}: {e}")
                similarities.append((0.0, i))
        
        # Sort by similarity (descending) and get top k
        similarities.sort(reverse=True)
        top_indices = [i for _, i in similarities[:k]]
        
        # Log retrieval stats
        top_similarities = [sim for sim, _ in similarities[:k]]
        logger.info(f"Retrieved {len(top_indices)} chunks with similarities: {top_similarities}")
        
        return [chunks[i] for i in top_indices]
    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        # Return first k chunks as fallback
        return chunks[:k] if chunks else [] 