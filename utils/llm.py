import google.generativeai as genai
import os

# Set your Gemini API key
GEMINI_API_KEY = "YOUR_API_KEY"
genai.configure(api_key=GEMINI_API_KEY)

MODEL_NAME = "gemini-1.5-flash-latest"

def generate_answer(question, context):
    prompt = (
        f"Answer the following question based only on the provided context.\n"
        f"Context:\n{context}\n"
        f"Question: {question}\n"
        f"Answer:"
    )
    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)
    return response.text.strip() if hasattr(response, 'text') else str(response) 