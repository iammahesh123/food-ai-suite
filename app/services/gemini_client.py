"""Google Gemini Client Wrapper with safe fallback mechanism."""
import os
import json
import logging
from typing import Optional, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)

_gemini_available = False
_model_instance = None

try:
    if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "your_gemini_api_key_here":
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        _model_instance = genai.GenerativeModel(settings.GEMINI_MODEL)
        _gemini_available = True
        logger.info(f"Initialized Gemini model: {settings.GEMINI_MODEL}")
    else:
        logger.info("No Gemini API key detected. Running in high-precision heuristic/semantic intelligence mode.")
except Exception as e:
    logger.warning(f"Failed to initialize Gemini SDK ({e}). Running in fallback mode.")
    _gemini_available = False

def is_gemini_active() -> bool:
    return _gemini_available and _model_instance is not None

def query_gemini_json(prompt: str, system_instruction: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Query Gemini and attempt to parse JSON response."""
    if not is_gemini_active():
        return None
    try:
        full_prompt = prompt
        if system_instruction:
            full_prompt = f"System Instruction: {system_instruction}\n\nTask:\n{prompt}\n\nRespond ONLY with valid JSON."
        else:
            full_prompt = f"{prompt}\n\nRespond ONLY with valid JSON."

        response = _model_instance.generate_content(full_prompt)
        text = response.text.strip()
        # Clean markdown codeblocks if present
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        return json.loads(text)
    except Exception as e:
        logger.warning(f"Gemini generation or JSON parse failed: {e}")
        return None
