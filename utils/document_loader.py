import requests
import tempfile
import os
from PyPDF2 import PdfReader
import docx

def parse_pdf(path):
    reader = PdfReader(path)
    return " ".join(page.extract_text() for page in reader.pages if page.extract_text())

def parse_docx(path):
    doc = docx.Document(path)
    return " ".join([para.text for para in doc.paragraphs])

def parse_email(path):
    # Placeholder: implement .eml parsing if needed
    return ""

def download_and_parse_document(url: str) -> str:
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("Document download failed")
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(response.content)
        tmp_path = tmp.name
    if url.endswith('.pdf'):
        text = parse_pdf(tmp_path)
    elif url.endswith('.docx'):
        text = parse_docx(tmp_path)
    elif url.endswith('.eml'):
        text = parse_email(tmp_path)
    else:
        raise Exception("Unsupported file type")
    os.remove(tmp_path)
    return text 