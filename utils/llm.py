import google.generativeai as genai
import os
import logging
import time
from typing import Optional
import json

logger = logging.getLogger(__name__)

# Set your Gemini API key from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY environment variable not set - using fallback mode")
    GEMINI_API_KEY = "dummy_key"  # Will cause fallback behavior

genai.configure(api_key=GEMINI_API_KEY)

MODEL_NAME = "gemini-1.5-flash-latest"
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds

class LLMError(Exception):
    """Custom exception for LLM errors"""
    pass

def create_prompt(question: str, context: str) -> str:
    """Create a well-structured prompt for the LLM"""
    return f"""You are an intelligent document analysis assistant. Answer the following question based ONLY on the provided context. If the context doesn't contain enough information to answer the question, say "I cannot answer this question based on the provided context."

Context:
{context}

Question: {question}

Answer:"""

def generate_answer_with_retry(question: str, context: str, max_retries: int = MAX_RETRIES) -> str:
    """Generate answer with retry logic and error handling"""
    
    if not context or not context.strip():
        return "I cannot answer this question as no relevant context was found."
    
    if not question or not question.strip():
        return "Please provide a valid question."
    
    # Truncate context if too long (Gemini has limits)
    max_context_length = 30000  # Conservative limit
    if len(context) > max_context_length:
        context = context[:max_context_length] + "... [truncated]"
        logger.warning(f"Context truncated to {max_context_length} characters")
    
    prompt = create_prompt(question, context)
    
    for attempt in range(max_retries):
        try:
            if GEMINI_API_KEY == "dummy_key":
                # Fallback mode for testing
                return f"Fallback response for: {question}"
            
            model = genai.GenerativeModel(MODEL_NAME)
            
            # Configure safety settings for better reliability
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            ]
            
            response = model.generate_content(
                prompt,
                safety_settings=safety_settings,
                generation_config={
                    "temperature": 0.3,  # Lower temperature for more consistent answers
                    "max_output_tokens": 1000,
                }
            )
            
            # Validate response
            if response and hasattr(response, 'text'):
                answer = response.text.strip()
                if answer:
                    logger.info(f"Generated answer successfully (attempt {attempt + 1})")
                    return answer
                else:
                    raise LLMError("Empty response from LLM")
            else:
                raise LLMError("Invalid response format from LLM")
                
        except Exception as e:
            logger.warning(f"LLM attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))  # Exponential backoff
            else:
                logger.error(f"All LLM attempts failed: {e}")
                return f"I apologize, but I encountered an error while processing your question. Please try again. Error: {str(e)}"
    
    return "I apologize, but I was unable to generate an answer. Please try again."

def generate_answer(question: str, context: str) -> str:
    """Main function to generate answer - wrapper for retry logic"""
    try:
        return generate_answer_with_retry(question, context)
    except Exception as e:
        logger.error(f"Unexpected error in generate_answer: {e}")
        return f"I apologize, but I encountered an unexpected error: {str(e)}"
