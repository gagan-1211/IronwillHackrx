import re
import logging
from typing import List

logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """Clean and normalize text for better chunking"""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters that might interfere with chunking
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)\[\]\{\}]', ' ', text)
    return text.strip()

def split_into_sentences(text: str) -> List[str]:
    """Split text into sentences using regex"""
    # Split on sentence endings, but preserve abbreviations
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Enhanced text chunking with semantic boundaries"""
    if not text or not text.strip():
        logger.warning("Empty text provided for chunking")
        return []
    
    # Clean the text
    text = clean_text(text)
    
    # Try sentence-based chunking first
    sentences = split_into_sentences(text)
    
    if len(sentences) <= 1:
        # Fallback to word-based chunking
        logger.info("Using word-based chunking")
        return chunk_by_words(text, chunk_size, overlap)
    
    # Use sentence-based chunking
    logger.info(f"Using sentence-based chunking with {len(sentences)} sentences")
    return chunk_by_sentences(sentences, chunk_size, overlap)

def chunk_by_sentences(sentences: List[str], chunk_size: int, overlap: int) -> List[str]:
    """Chunk text by sentences while respecting size limits"""
    chunks = []
    current_chunk = []
    current_size = 0
    
    for sentence in sentences:
        sentence_size = len(sentence.split())
        
        # If adding this sentence would exceed chunk size
        if current_size + sentence_size > chunk_size and current_chunk:
            # Save current chunk
            chunk_text = " ".join(current_chunk)
            if chunk_text.strip():
                chunks.append(chunk_text)
            
            # Start new chunk with overlap
            overlap_sentences = current_chunk[-2:] if len(current_chunk) >= 2 else current_chunk
            current_chunk = overlap_sentences + [sentence]
            current_size = sum(len(s.split()) for s in current_chunk)
        else:
            # Add sentence to current chunk
            current_chunk.append(sentence)
            current_size += sentence_size
    
    # Add final chunk
    if current_chunk:
        chunk_text = " ".join(current_chunk)
        if chunk_text.strip():
            chunks.append(chunk_text)
    
    logger.info(f"Created {len(chunks)} chunks from {len(sentences)} sentences")
    return chunks

def chunk_by_words(text: str, chunk_size: int, overlap: int) -> List[str]:
    """Fallback word-based chunking"""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    
    logger.info(f"Created {len(chunks)} word-based chunks")
    return chunks

def validate_chunks(chunks: List[str]) -> List[str]:
    """Validate and filter chunks"""
    valid_chunks = []
    for i, chunk in enumerate(chunks):
        if chunk and len(chunk.strip()) > 10:  # Minimum meaningful chunk size
            valid_chunks.append(chunk)
        else:
            logger.warning(f"Removed invalid chunk {i}: too short or empty")
    
    logger.info(f"Validated {len(valid_chunks)} chunks from {len(chunks)} total")
    return valid_chunks 