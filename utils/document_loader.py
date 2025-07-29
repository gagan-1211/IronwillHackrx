import requests
import tempfile
import os
import logging
from typing import Optional
from urllib.parse import urlparse
import mimetypes
from PyPDF2 import PdfReader
import docx
import json

logger = logging.getLogger(__name__)

class DocumentLoadError(Exception):
    """Custom exception for document loading errors"""
    pass

def get_file_extension(url: str) -> str:
    """Extract file extension from URL"""
    parsed = urlparse(url)
    path = parsed.path.lower()
    if '.' in path:
        return path.split('.')[-1]
    return ''

def get_content_type(url: str) -> Optional[str]:
    """Get content type from URL or headers"""
    try:
        response = requests.head(url, timeout=10)
        content_type = response.headers.get('content-type', '').lower()
        if content_type:
            return content_type
    except Exception as e:
        logger.warning(f"Could not get content type for {url}: {e}")
    
    # Fallback to URL extension
    ext = get_file_extension(url)
    if ext == 'pdf':
        return 'application/pdf'
    elif ext == 'docx':
        return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    elif ext == 'txt':
        return 'text/plain'
    elif ext == 'json':
        return 'application/json'
    return None

def parse_pdf(path: str) -> str:
    """Parse PDF file with error handling"""
    try:
        reader = PdfReader(path)
        text_parts = []
        for i, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    text_parts.append(page_text)
            except Exception as e:
                logger.warning(f"Failed to extract text from page {i}: {e}")
        return " ".join(text_parts)
    except Exception as e:
        raise DocumentLoadError(f"Failed to parse PDF: {e}")

def parse_docx(path: str) -> str:
    """Parse DOCX file with error handling"""
    try:
        doc = docx.Document(path)
        text_parts = []
        for para in doc.paragraphs:
            if para.text and para.text.strip():
                text_parts.append(para.text)
        return " ".join(text_parts)
    except Exception as e:
        raise DocumentLoadError(f"Failed to parse DOCX: {e}")

def parse_txt(path: str) -> str:
    """Parse text file with error handling"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            with open(path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception as e:
            raise DocumentLoadError(f"Failed to parse text file: {e}")
    except Exception as e:
        raise DocumentLoadError(f"Failed to parse text file: {e}")

def parse_json(path: str) -> str:
    """Parse JSON file and extract text content"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Try to extract text from common JSON structures
            if isinstance(data, dict):
                text_parts = []
                for key, value in data.items():
                    if isinstance(value, str):
                        text_parts.append(f"{key}: {value}")
                    elif isinstance(value, (dict, list)):
                        text_parts.append(f"{key}: {json.dumps(value)}")
                return " ".join(text_parts)
            elif isinstance(data, list):
                return " ".join(str(item) for item in data)
            else:
                return str(data)
    except Exception as e:
        raise DocumentLoadError(f"Failed to parse JSON: {e}")

def parse_email(path: str) -> str:
    """Parse email file (.eml) with basic text extraction"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Simple email parsing - extract body after headers
            if '\n\n' in content:
                headers, body = content.split('\n\n', 1)
                return body
            return content
    except Exception as e:
        raise DocumentLoadError(f"Failed to parse email: {e}")

def download_and_parse_document(url: str) -> str:
    """Download and parse document with comprehensive error handling"""
    logger.info(f"Downloading document from: {url}")
    
    # Validate URL
    if not url.startswith(('http://', 'https://')):
        raise DocumentLoadError("Invalid URL: must start with http:// or https://")
    
    try:
        # Download document with timeout and headers
        headers = {
            'User-Agent': 'HackRx-Document-Loader/1.0'
        }
        response = requests.get(url, headers=headers, timeout=30, stream=True)
        response.raise_for_status()
        
        # Check file size (limit to 50MB for Vercel)
        content_length = response.headers.get('content-length')
        if content_length and int(content_length) > 50 * 1024 * 1024:
            raise DocumentLoadError("File too large (max 50MB)")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(response.content)
            tmp_path = tmp.name
        
        try:
            # Determine file type and parse
            content_type = get_content_type(url)
            file_extension = get_file_extension(url)
            
            logger.info(f"File type: {content_type}, extension: {file_extension}")
            
            # Parse based on content type or extension
            if content_type == 'application/pdf' or file_extension == 'pdf':
                text = parse_pdf(tmp_path)
            elif content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' or file_extension == 'docx':
                text = parse_docx(tmp_path)
            elif content_type == 'text/plain' or file_extension == 'txt':
                text = parse_txt(tmp_path)
            elif content_type == 'application/json' or file_extension == 'json':
                text = parse_json(tmp_path)
            elif file_extension == 'eml':
                text = parse_email(tmp_path)
            else:
                # Try to guess from content
                if response.content.startswith(b'%PDF'):
                    text = parse_pdf(tmp_path)
                elif 'PK' in response.content[:4]:  # ZIP/DOCX signature
                    text = parse_docx(tmp_path)
                else:
                    # Try as text
                    text = parse_txt(tmp_path)
            
            if not text or not text.strip():
                raise DocumentLoadError("No text content extracted from document")
            
            logger.info(f"Successfully parsed document, extracted {len(text)} characters")
            return text.strip()
            
        finally:
            # Clean up temporary file
            try:
                os.remove(tmp_path)
            except Exception as e:
                logger.warning(f"Failed to remove temp file: {e}")
                
    except requests.exceptions.RequestException as e:
        raise DocumentLoadError(f"Failed to download document: {e}")
    except Exception as e:
        raise DocumentLoadError(f"Failed to process document: {e}") 