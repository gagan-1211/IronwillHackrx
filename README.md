<<<<<<< HEAD
# HackRx 6.0 Intelligent Query–Retrieval System

## Overview
This project implements a hackathon-compliant, LLM-powered intelligent query–retrieval system for HackRx 6.0. It processes large documents (PDF, DOCX, email), answers natural language queries, and provides accurate, explainable answers using semantic search and LLM reasoning.

## Features
- Accepts document URL and questions via POST `/hackrx/run`
- Supports PDF, DOCX, and email parsing
- Uses FAISS for fast semantic search
- Embeds text with HuggingFace sentence-transformers (can swap for Gemini/OpenAI)
- Modular, extensible, and cloud-ready
- Strictly follows HackRx 6.0 input/output and security requirements

## Setup
1. **Clone the repository**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Set API token (optional):**
   - By default, the token is `your_token_here`. Set `API_TOKEN` env variable to change.
4. **Run the server:**
   ```bash
   uvicorn main:app --reload
   ```

## Usage
- **Endpoint:** `POST /hackrx/run`
- **Headers:**
  - `Authorization: Bearer <your_token_here>`
- **Request Body:**
  ```json
  {
    "documents": "<url to PDF/DOCX/email>",
    "questions": ["Question 1", "Question 2"]
  }
  ```
- **Response:**
  ```json
  {
    "answers": ["Answer 1", "Answer 2"]
  }
  ```

## Hackathon Compliance
- Input/output format matches HackRx 6.0 requirements
- Modular code for reusability and extensibility
- Security via Bearer token
- Ready for cloud deployment (FastAPI + Uvicorn)

## Customization
- Swap out `utils/llm.py` for Gemini, GPT-4, or HuggingFace LLM as needed
- Extend `utils/document_loader.py` for more file types
- Adjust chunking/embedding parameters in `utils/chunker.py` and `utils/embedder.py`

## License
=======
# HackRx 6.0 Intelligent Query–Retrieval System

## Overview
This project implements a hackathon-compliant, LLM-powered intelligent query–retrieval system for HackRx 6.0. It processes large documents (PDF, DOCX, email), answers natural language queries, and provides accurate, explainable answers using semantic search and LLM reasoning.

## Features
- Accepts document URL and questions via POST `/hackrx/run`
- Supports PDF, DOCX, and email parsing
- Uses FAISS for fast semantic search
- Embeds text with HuggingFace sentence-transformers (can swap for Gemini/OpenAI)
- Modular, extensible, and cloud-ready
- Strictly follows HackRx 6.0 input/output and security requirements

## Setup
1. **Clone the repository**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Set API token (optional):**
   - By default, the token is `your_token_here`. Set `API_TOKEN` env variable to change.
4. **Run the server:**
   ```bash
   uvicorn main:app --reload
   ```

## Usage
- **Endpoint:** `POST /hackrx/run`
- **Headers:**
  - `Authorization: Bearer <your_token_here>`
- **Request Body:**
  ```json
  {
    "documents": "<url to PDF/DOCX/email>",
    "questions": ["Question 1", "Question 2"]
  }
  ```
- **Response:**
  ```json
  {
    "answers": ["Answer 1", "Answer 2"]
  }
  ```

## Hackathon Compliance
- Input/output format matches HackRx 6.0 requirements
- Modular code for reusability and extensibility
- Security via Bearer token
- Ready for cloud deployment (FastAPI + Uvicorn)

## Customization
- Swap out `utils/llm.py` for Gemini, GPT-4, or HuggingFace LLM as needed
- Extend `utils/document_loader.py` for more file types
- Adjust chunking/embedding parameters in `utils/chunker.py` and `utils/embedder.py`

## License
>>>>>>> a273322c99372dd5afe05f3c8fd2501ce33c1578
MIT 