# HackRx 6.0 Intelligent Query–Retrieval System v2.0

## Overview
This project implements a hackathon-compliant, LLM-powered intelligent query–retrieval system for HackRx 6.0. It processes large documents (PDF, DOCX, TXT, JSON, email), answers natural language queries, and provides accurate, explainable answers using advanced semantic search and LLM reasoning.

## 🚀 Enhanced Features (v2.0)

### Core Improvements
- ✅ **Advanced Semantic Search**: Sentence transformer embeddings with fallback to word frequency
- ✅ **Comprehensive Error Handling**: Robust error handling with detailed logging
- ✅ **Intelligent Caching**: In-memory cache with TTL for improved performance
- ✅ **Multiple File Types**: Support for PDF, DOCX, TXT, JSON, and email files
- ✅ **Enhanced Logging**: Structured logging with request/response tracking
- ✅ **Health Monitoring**: Built-in health checks and cache statistics
- ✅ **Vercel Optimization**: Optimized for serverless deployment constraints

### New Capabilities
- 🔄 **Retry Logic**: Automatic retry with exponential backoff for LLM calls
- 📊 **Performance Metrics**: Processing time tracking and metadata
- 🛡️ **Input Validation**: Comprehensive request validation
- 🧹 **Text Processing**: Advanced text cleaning and chunking
- 📈 **Monitoring**: Request logging, error tracking, and performance metrics
- 🔧 **Cache Management**: Cache statistics and manual cache clearing

## Setup

### 1. **Clone the repository**
```bash
git clone <repository-url>
cd bajaj
```

### 2. **Install dependencies**
```bash
pip install -r requirements.txt
```

### 3. **Set environment variables**
```bash
# Required for LLM functionality
export GEMINI_API_KEY="your_gemini_api_key_here"

# Optional - change default token
export API_TOKEN="your_custom_token_here"
```

### 4. **Run the server**
```bash
# Development
uvicorn main:app --reload

# Production
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Main Endpoint
- **POST** `/hackrx/run` - Process documents and answer questions

### Health & Monitoring
- **GET** `/health` - Health check with cache status
- **GET** `/cache/stats` - Cache statistics
- **DELETE** `/cache/clear` - Clear cache

### Utility Endpoints
- **GET** `/` - Root endpoint
- **GET** `/test` - Test endpoint

## Usage Examples

### Basic Document Analysis
```bash
curl -X POST "https://your-api-url/hackrx/run" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token_here" \
  -d '{
    "documents": "https://example.com/document.pdf",
    "questions": [
      "What are the main policies in this document?",
      "What are the key requirements?"
    ]
  }'
```

### Response Format
```json
{
  "answers": [
    "The main policies include...",
    "Key requirements are..."
  ],
  "metadata": {
    "document_url": "https://example.com/document.pdf",
    "num_questions": 2,
    "num_chunks": 15,
    "processing_time": 3.45,
    "cache_hit": false
  }
}
```

## Supported File Types

| Type | Extension | Description |
|------|-----------|-------------|
| PDF | `.pdf` | Portable Document Format |
| Word | `.docx` | Microsoft Word documents |
| Text | `.txt` | Plain text files |
| JSON | `.json` | JSON data files |
| Email | `.eml` | Email message files |

## Configuration

### Environment Variables
- `GEMINI_API_KEY`: Google Gemini API key (required for LLM)
- `API_TOKEN`: Custom API token (default: "your_token_here")

### Limits
- **Document Size**: 50MB maximum
- **Text Length**: 1MB maximum extracted text
- **Questions**: 10 maximum per request
- **Cache TTL**: 1 hour (configurable)

## Testing

### Run Enhanced Test Suite
```powershell
# Windows PowerShell
.\test_enhanced.ps1
```

### Manual Testing
```bash
# Health check
curl https://your-api-url/health

# Cache stats
curl -H "Authorization: Bearer your_token" https://your-api-url/cache/stats

# Clear cache
curl -X DELETE -H "Authorization: Bearer your_token" https://your-api-url/cache/clear
```

## Architecture

### Components
1. **Document Loader** (`utils/document_loader.py`)
   - Multi-format document parsing
   - Robust error handling
   - File size validation

2. **Text Processor** (`utils/chunker.py`)
   - Sentence-based chunking
   - Text cleaning and validation
   - Semantic boundary detection

3. **Embedding System** (`utils/embedder.py`)
   - Sentence transformer embeddings
   - Fallback to word frequency
   - Cosine similarity calculation

4. **Search Engine** (`utils/faiss_index.py`)
   - Vector similarity search
   - Top-k retrieval
   - Performance logging

5. **LLM Interface** (`utils/llm.py`)
   - Google Gemini integration
   - Retry logic with backoff
   - Response validation

### Data Flow
```
Document URL → Download & Parse → Chunk Text → Embed Chunks → Build Index
                                                                    ↓
Questions → Embed Query → Retrieve Similar Chunks → Generate Answer → Cache Response
```

## Deployment

### Vercel Deployment
The application is optimized for Vercel serverless deployment:

- **Memory**: 3008MB allocated
- **Timeout**: 60 seconds maximum
- **Package Size**: 50MB limit
- **Cold Start**: Optimized with lazy loading

### Environment Setup
1. Set `GEMINI_API_KEY` in Vercel environment variables
2. Optionally set `API_TOKEN` for custom authentication
3. Deploy using Vercel CLI or GitHub integration

## Performance Optimizations

### Caching Strategy
- **In-Memory Cache**: Fast response for repeated queries
- **TTL Management**: Automatic cache expiration
- **Cache Statistics**: Monitoring and management endpoints

### Memory Management
- **Lazy Loading**: Models loaded on first use
- **Text Truncation**: Limits context size for LLM
- **Chunk Validation**: Filters out invalid chunks

### Error Handling
- **Graceful Degradation**: Fallback to simpler methods
- **Detailed Logging**: Structured logs for debugging
- **User-Friendly Errors**: Clear error messages

## Monitoring & Logging

### Structured Logging
- Request/response tracking
- Performance metrics
- Error categorization
- JSON format for easy parsing

### Health Monitoring
- Application health status
- Cache statistics
- Memory usage tracking
- Response time monitoring

## Security Features

- **Bearer Token Authentication**: Secure API access
- **Input Validation**: Comprehensive request validation
- **File Size Limits**: Prevents abuse
- **Content Type Validation**: Secure file processing

## Customization

### LLM Integration
- Swap `utils/llm.py` for different LLM providers
- Configure retry logic and timeouts
- Adjust safety settings and generation parameters

### Embedding Models
- Change `MODEL_NAME` in `utils/embedder.py`
- Implement custom embedding functions
- Add new similarity metrics

### Document Processing
- Extend `utils/document_loader.py` for new file types
- Implement custom text cleaning
- Add document preprocessing steps

## Troubleshooting

### Common Issues
1. **Memory Errors**: Reduce chunk size or document size
2. **Timeout Errors**: Check network connectivity and document size
3. **Embedding Failures**: Verify sentence-transformers installation
4. **LLM Errors**: Check API key and network connectivity

### Debug Mode
Enable detailed logging by setting log level:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## License
MIT License - See LICENSE file for details

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

**Version**: 2.0.0  
**Last Updated**: December 2024  
**Compatibility**: HackRx 6.0 Requirements 