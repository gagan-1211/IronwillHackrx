# HackRx 6.0 Deployment Guide

## Overview
This guide covers deploying the enhanced HackRx 6.0 system to various platforms, with a focus on Vercel serverless deployment.

## 🚀 Quick Deploy to Vercel

### 1. Prerequisites
- GitHub account
- Vercel account (free tier available)
- Google Gemini API key

### 2. One-Click Deploy
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/your-username/bajaj)

### 3. Manual Deployment Steps

#### Step 1: Prepare Repository
```bash
# Clone your repository
git clone https://github.com/your-username/bajaj.git
cd bajaj

# Ensure all files are committed
git add .
git commit -m "Enhanced HackRx 6.0 system"
git push origin main
```

#### Step 2: Deploy to Vercel
```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

#### Step 3: Configure Environment Variables
In your Vercel dashboard:
1. Go to your project settings
2. Navigate to "Environment Variables"
3. Add the following variables:

```
GEMINI_API_KEY=your_gemini_api_key_here
API_TOKEN=your_custom_token_here  # Optional
```

## 🔧 Local Development Setup

### 1. Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file:
```env
GEMINI_API_KEY=your_gemini_api_key_here
API_TOKEN=your_custom_token_here
```

### 3. Run Development Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📊 Monitoring & Testing

### 1. Health Check
```bash
curl https://your-vercel-url.vercel.app/health
```

### 2. Run Test Suite
```powershell
# Windows PowerShell
.\test_enhanced.ps1

# Or run monitoring script
python monitor.py
```

### 3. Manual API Testing
```bash
curl -X POST "https://your-vercel-url.vercel.app/hackrx/run" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_token_here" \
  -d '{
    "documents": "https://example.com/document.pdf",
    "questions": ["What is this document about?"]
  }'
```

## 🐳 Docker Deployment

### 1. Create Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Build and Run
```bash
# Build image
docker build -t hackrx-api .

# Run container
docker run -p 8000:8000 \
  -e GEMINI_API_KEY=your_key \
  -e API_TOKEN=your_token \
  hackrx-api
```

## ☁️ Cloud Platform Deployments

### AWS Lambda (via Serverless Framework)

#### 1. Install Serverless Framework
```bash
npm install -g serverless
```

#### 2. Create serverless.yml
```yaml
service: hackrx-api

provider:
  name: aws
  runtime: python3.9
  region: us-east-1
  environment:
    GEMINI_API_KEY: ${env:GEMINI_API_KEY}
    API_TOKEN: ${env:API_TOKEN}

functions:
  api:
    handler: main.handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
    timeout: 60
    memorySize: 3008

plugins:
  - serverless-python-requirements

custom:
  pythonRequirements:
    dockerizePip: true
    layer:
      name: python-deps
      description: Python dependencies for HackRx API
```

#### 3. Deploy
```bash
serverless deploy
```

### Google Cloud Run

#### 1. Create Dockerfile (same as above)

#### 2. Build and Deploy
```bash
# Build image
docker build -t gcr.io/your-project/hackrx-api .

# Push to Google Container Registry
docker push gcr.io/your-project/hackrx-api

# Deploy to Cloud Run
gcloud run deploy hackrx-api \
  --image gcr.io/your-project/hackrx-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --timeout 60
```

### Azure Functions

#### 1. Install Azure Functions Core Tools
```bash
npm install -g azure-functions-core-tools@4
```

#### 2. Create Function App
```bash
func init hackrx-api --python
cd hackrx-api
```

#### 3. Create function.json
```json
{
  "scriptFile": "main.py",
  "bindings": [
    {
      "authLevel": "anonymous",
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "methods": ["GET", "POST"],
      "route": "{*route}"
    },
    {
      "type": "http",
      "direction": "out",
      "name": "$return"
    }
  ]
}
```

#### 4. Deploy
```bash
func azure functionapp publish your-function-app-name
```

## 🔍 Performance Optimization

### 1. Vercel-Specific Optimizations
- **Memory**: 3008MB allocated (maximum for Vercel)
- **Timeout**: 60 seconds (maximum for Vercel)
- **Package Size**: Keep under 50MB
- **Cold Start**: Lazy loading of models

### 2. Caching Strategy
- **In-Memory Cache**: Fast response for repeated queries
- **TTL Management**: 1-hour cache expiration
- **Cache Statistics**: Monitor cache hit rates

### 3. Error Handling
- **Graceful Degradation**: Fallback to simpler methods
- **Retry Logic**: Exponential backoff for LLM calls
- **User-Friendly Errors**: Clear error messages

## 📈 Monitoring & Logging

### 1. Vercel Analytics
- Built-in request/response logging
- Performance metrics
- Error tracking

### 2. Custom Monitoring
```bash
# Run monitoring script
python monitor.py

# Check logs
vercel logs your-project-name
```

### 3. Health Checks
```bash
# Automated health checks
curl https://your-api-url/health

# Cache statistics
curl -H "Authorization: Bearer your_token" https://your-api-url/cache/stats
```

## 🔒 Security Considerations

### 1. API Token Management
- Use strong, unique tokens
- Rotate tokens regularly
- Store tokens securely

### 2. Input Validation
- Validate all inputs
- Sanitize URLs
- Check file sizes

### 3. Rate Limiting
Consider implementing rate limiting for production:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Memory Errors
**Symptoms**: `MemoryError` or function timeout
**Solutions**:
- Reduce chunk size in `utils/chunker.py`
- Limit document size
- Use smaller embedding model

#### 2. Timeout Errors
**Symptoms**: 504 Gateway Timeout
**Solutions**:
- Check document size (max 50MB)
- Verify network connectivity
- Optimize chunking parameters

#### 3. Embedding Failures
**Symptoms**: `ModuleNotFoundError` for sentence-transformers
**Solutions**:
- Ensure all dependencies are installed
- Check Vercel package size limits
- Use fallback embedding method

#### 4. LLM Errors
**Symptoms**: Gemini API errors
**Solutions**:
- Verify API key is correct
- Check API quotas and limits
- Implement retry logic

### Debug Mode
Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📋 Deployment Checklist

- [ ] All dependencies installed
- [ ] Environment variables configured
- [ ] API keys set up
- [ ] Health check passes
- [ ] Test suite runs successfully
- [ ] Monitoring configured
- [ ] Error handling tested
- [ ] Performance optimized
- [ ] Security measures in place
- [ ] Documentation updated

## 🎯 Production Readiness

### Performance Benchmarks
- **Response Time**: < 30 seconds for typical documents
- **Memory Usage**: < 3GB peak
- **Cache Hit Rate**: > 50% for repeated queries
- **Error Rate**: < 1%

### Monitoring Metrics
- Request/response times
- Memory usage
- Cache hit rates
- Error rates
- API usage patterns

### Backup & Recovery
- Regular backups of configuration
- Environment variable backups
- API key rotation procedures
- Rollback procedures

---

**Last Updated**: December 2024  
**Version**: 2.0.0  
**Compatibility**: HackRx 6.0 Requirements 