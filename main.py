from fastapi import FastAPI, Request, HTTPException, Header
from pydantic import BaseModel
from typing import List, Optional
import os

from utils.document_loader import download_and_parse_document
from utils.chunker import chunk_text
from utils.embedder import embed_chunks, embed_query
from utils.faiss_index import build_faiss_index, retrieve_top_k_chunks
from utils.llm import generate_answer

app = FastAPI()

API_TOKEN = os.getenv("API_TOKEN", "your_token_here")

class QueryRequest(BaseModel):
    documents: str
    questions: List[str]

class QueryResponse(BaseModel):
    answers: List[str]

def check_token(auth_header: str):
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = auth_header.split(" ")[1]
    if token != API_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid token")

@app.post("/hackrx/run", response_model=QueryResponse)
async def hackrx_run(
    req: QueryRequest,
    authorization: Optional[str] = Header(None)
):
    check_token(authorization)
    # 1. Download and parse document
    text = download_and_parse_document(req.documents)
    # 2. Chunk and embed
    chunks = chunk_text(text)
    chunk_embeddings = embed_chunks(chunks)
    faiss_index = build_faiss_index(chunk_embeddings)
    # 3. For each question, retrieve and answer
    answers = []
    for question in req.questions:
        q_embedding = embed_query(question)
        top_chunks = retrieve_top_k_chunks(faiss_index, q_embedding, chunks)
        context = " ".join(top_chunks)
        answer = generate_answer(question, context)
        answers.append(answer)
    return QueryResponse(answers=answers) 