import faiss
import numpy as np

def build_faiss_index(embeddings):
    dim = embeddings[0].shape[0] if hasattr(embeddings[0], 'shape') else len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings))
    return index

def retrieve_top_k_chunks(index, query_embedding, chunks, k=3):
    D, I = index.search(np.array([query_embedding]), k)
    return [chunks[i] for i in I[0]] 