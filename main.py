from fastapi import FastAPI, Request, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Any
import os
import time
import logging
import structlog
import hashlib
import json
from datetime import datetime, timedelta
import asyncio

# Import our utilities
from utils.document_loader import download_and_parse_document, DocumentLoadError
from utils.chunker import chunk_text, validate_chunks
from utils.embedder import embed_chunks, embed_query
from utils.faiss_index import build_faiss_index, retrieve_top_k_chunks
from utils.llm import generate_answer, LLMError

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Initialize FastAPI app
app = FastAPI(
    title="HackRx 6.0 Intelligent Query-Retrieval System",
    description="LLM-powered document analysis and question answering system",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
API_TOKEN = os.getenv("API_TOKEN", "your_token_here")
MAX_DOCUMENT_SIZE = 50 * 1024 * 1024  # 50MB
MAX_QUESTIONS = 10
MAX_TEXT_LENGTH = 1000000  # 1MB text limit

# Simple in-memory cache (for Vercel, consider Redis for production)
cache: Dict[str, Any] = {}
CACHE_TTL = 3600  # 1 hour

class QueryRequest(BaseModel):
    documents: str
    questions: List[str]
    
    @validator('documents')
    def validate_documents(cls, v):
        if not v or not v.strip():
            raise ValueError("Document URL cannot be empty")
        if not v.startswith(('http://', 'https://')):
            raise ValueError("Document URL must start with http:// or https://")
        return v.strip()
    
    @validator('questions')
    def validate_questions(cls, v):
        if not v:
            raise ValueError("At least one question is required")
        if len(v) > MAX_QUESTIONS:
            raise ValueError(f"Maximum {MAX_QUESTIONS} questions allowed")
        for i, question in enumerate(v):
            if not question or not question.strip():
                raise ValueError(f"Question {i+1} cannot be empty")
        return [q.strip() for q in v]

class QueryResponse(BaseModel):
    answers: List[str]
    metadata: Dict[str, Any]

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    cache_size: int

def check_token(auth_header: Optional[str] = Header(None)):
    """Validate API token"""
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = auth_header.split(" ")[1]
    if token != API_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")

def get_cache_key(documents: str, questions: List[str]) -> str:
    """Generate cache key for request"""
    content = f"{documents}:{json.dumps(questions, sort_keys=True)}"
    return hashlib.md5(content.encode()).hexdigest()

def is_cache_valid(cache_entry: Dict[str, Any]) -> bool:
    """Check if cache entry is still valid"""
    if 'timestamp' not in cache_entry:
        return False
    cache_time = datetime.fromisoformat(cache_entry['timestamp'])
    return datetime.now() - cache_time < timedelta(seconds=CACHE_TTL)

def cleanup_cache():
    """Remove expired cache entries"""
    global cache
    current_time = datetime.now()
    expired_keys = []
    
    for key, entry in cache.items():
        if 'timestamp' in entry:
            cache_time = datetime.fromisoformat(entry['timestamp'])
            if current_time - cache_time >= timedelta(seconds=CACHE_TTL):
                expired_keys.append(key)
    
    for key in expired_keys:
        del cache[key]
    
    if expired_keys:
        logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and responses"""
    start_time = time.time()
    
    # Log request
    logger.info(
        "Request started",
        method=request.method,
        url=str(request.url),
        client_ip=request.client.host if request.client else None
    )
    
    try:
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            "Request completed",
            status_code=response.status_code,
            process_time=process_time
        )
        
        return response
    except Exception as e:
        # Log error
        process_time = time.time() - start_time
        logger.error(
            "Request failed",
            error=str(e),
            process_time=process_time
        )
        raise

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(
        "Unhandled exception",
        error=str(exc),
        url=str(request.url),
        method=request.method
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again."
        }
    )

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {"message": "HackRx 6.0 API is running!", "version": "2.0.0"}

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with cache status"""
    cleanup_cache()
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="2.0.0",
        cache_size=len(cache)
    )

@app.get("/test")
async def test():
    """Test endpoint"""
    return {"status": "ok", "message": "Test endpoint working", "timestamp": datetime.now().isoformat()}

@app.post("/hackrx/run", response_model=QueryResponse)
async def hackrx_run(
    req: QueryRequest,
    authorization: Optional[str] = Header(None)
):
    """Main endpoint for document analysis and question answering"""
    
    # Validate token
    check_token(authorization)
    
    # Check cache first
    cache_key = get_cache_key(req.documents, req.questions)
    if cache_key in cache and is_cache_valid(cache[cache_key]):
        logger.info("Returning cached response", cache_key=cache_key)
        return QueryResponse(**cache[cache_key]['response'])
    
    start_time = time.time()
    
    try:
        # Step 1: Download and parse document
        logger.info("Starting document processing", url=req.documents)
        text = download_and_parse_document(req.documents)
        
        if len(text) > MAX_TEXT_LENGTH:
            raise HTTPException(
                status_code=400, 
                detail=f"Document too large. Maximum {MAX_TEXT_LENGTH} characters allowed."
            )
        
        # Step 2: Chunk and embed
        logger.info("Chunking document", text_length=len(text))
        chunks = chunk_text(text)
        chunks = validate_chunks(chunks)
        
        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No valid text content could be extracted from the document"
            )
        
        logger.info("Embedding chunks", num_chunks=len(chunks))
        chunk_embeddings = embed_chunks(chunks)
        faiss_index = build_faiss_index(chunk_embeddings)
        
        # Step 3: Process each question
        answers = []
        metadata = {
            "document_url": req.documents,
            "num_questions": len(req.questions),
            "num_chunks": len(chunks),
            "processing_time": 0,
            "cache_hit": False
        }
        
        for i, question in enumerate(req.questions):
            logger.info(f"Processing question {i+1}/{len(req.questions)}", question=question)
            
            try:
                q_embedding = embed_query(question)
                top_chunks = retrieve_top_k_chunks(faiss_index, q_embedding, chunks)
                context = " ".join(top_chunks)
                
                answer = generate_answer(question, context)
                answers.append(answer)
                
                logger.info(f"Generated answer for question {i+1}", answer_length=len(answer))
                
            except Exception as e:
                logger.error(f"Failed to process question {i+1}", error=str(e))
                answers.append(f"I apologize, but I encountered an error while processing this question: {str(e)}")
        
        # Calculate processing time
        processing_time = time.time() - start_time
        metadata["processing_time"] = processing_time
        
        # Create response
        response_data = {
            "answers": answers,
            "metadata": metadata
        }
        
        # Cache the response
        cache[cache_key] = {
            "response": response_data,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(
            "Request completed successfully",
            processing_time=processing_time,
            num_answers=len(answers)
        )
        
        return QueryResponse(**response_data)
        
    except DocumentLoadError as e:
        logger.error("Document loading failed", error=str(e))
        raise HTTPException(status_code=400, detail=f"Document processing failed: {str(e)}")
    
    except LLMError as e:
        logger.error("LLM processing failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Answer generation failed: {str(e)}")
    
    except Exception as e:
        logger.error("Unexpected error in hackrx_run", error=str(e))
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@app.delete("/cache/clear")
async def clear_cache(authorization: Optional[str] = Header(None)):
    """Clear the cache"""
    check_token(authorization)
    global cache
    cache_size = len(cache)
    cache.clear()
    logger.info("Cache cleared", cache_size=cache_size)
    return {"message": f"Cache cleared. Removed {cache_size} entries."}

@app.get("/cache/stats")
async def cache_stats(authorization: Optional[str] = Header(None)):
    """Get cache statistics"""
    check_token(authorization)
    cleanup_cache()
    return {
        "cache_size": len(cache),
        "cache_ttl": CACHE_TTL,
        "max_document_size": MAX_DOCUMENT_SIZE,
        "max_questions": MAX_QUESTIONS
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("HackRx 6.0 API starting up", version="2.0.0")
    
    # Validate configuration
    if API_TOKEN == "your_token_here":
        logger.warning("Using default API token - consider setting API_TOKEN environment variable")
    
    # Check for required environment variables
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        logger.warning("GEMINI_API_KEY not set - LLM will use fallback mode")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("HackRx 6.0 API shutting down")
    cleanup_cache() 