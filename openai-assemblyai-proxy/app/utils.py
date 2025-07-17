import logging
import os
from typing import Optional, List, Dict, Any
from datetime import datetime


def setup_logging():
    """Setup structured logging"""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


def map_language_code(openai_language: Optional[str]) -> Optional[str]:
    """Map OpenAI language codes to AssemblyAI language codes"""
    if not openai_language:
        return None
    
    # Basic mapping - AssemblyAI uses ISO 639-1 codes
    language_mapping = {
        "en": "en",
        "es": "es", 
        "fr": "fr",
        "de": "de",
        "it": "it",
        "pt": "pt",
        "nl": "nl",
        "ja": "ja",
        "ko": "ko",
        "zh": "zh",
        "ru": "ru",
        "ar": "ar",
        "hi": "hi",
        "tr": "tr",
        "pl": "pl",
        "uk": "uk",
        "vi": "vi",
        "ms": "ms",
        "th": "th",
        "fi": "fi",
        "da": "da",
        "no": "no",
        "sv": "sv"
    }
    
    return language_mapping.get(openai_language.lower(), openai_language.lower())


def parse_word_boost(prompt: Optional[str]) -> Optional[List[str]]:
    """Parse OpenAI prompt into AssemblyAI word_boost array"""
    if not prompt:
        return None
    
    # Split by spaces and commas, filter empty strings
    words = [word.strip() for word in prompt.replace(",", " ").split() if word.strip()]
    return words if words else None


def format_openai_error(message: str, error_type: str = "invalid_request_error", code: Optional[str] = None) -> Dict[str, Any]:
    """Format error response in OpenAI format"""
    error_data = {
        "message": message,
        "type": error_type
    }
    
    if code:
        error_data["code"] = code
    
    return {"error": error_data}


def convert_assemblyai_to_openai_response(assemblyai_response: Dict[str, Any], response_format: str = "json") -> Dict[str, Any]:
    """Convert AssemblyAI response to OpenAI format"""
    if response_format == "text":
        return assemblyai_response.get("text", "")
    
    # Build OpenAI-compatible response
    openai_response = {
        "text": assemblyai_response.get("text", ""),
        "task": "transcribe",
        "language": assemblyai_response.get("language_code"),
        "duration": assemblyai_response.get("audio_duration")
    }
    
    # Convert words to segments if available
    if assemblyai_response.get("words"):
        segments = []
        for word in assemblyai_response["words"]:
            segment = {
                "id": len(segments),
                "seek": word.get("start", 0),
                "start": word.get("start", 0) / 1000.0,  # Convert ms to seconds
                "end": word.get("end", 0) / 1000.0,
                "text": word.get("text", ""),
                "tokens": [],
                "temperature": 0.0,
                "avg_logprob": 0.0,
                "compression_ratio": 1.0,
                "no_speech_prob": 0.0
            }
            segments.append(segment)
        openai_response["segments"] = segments
    
    return openai_response


def validate_audio_url(url: str) -> bool:
    """Basic validation for audio URL"""
    if not url:
        return False
    
    # Check if it's a valid URL format
    if not url.startswith(("http://", "https://")):
        return False
    
    # Check for common audio file extensions
    audio_extensions = [".wav", ".mp3", ".m4a", ".flac", ".ogg", ".aac", ".wma"]
    url_lower = url.lower()
    
    # Either has audio extension or could be a streaming URL
    return any(ext in url_lower for ext in audio_extensions) or "audio" in url_lower


def get_current_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.utcnow().isoformat() + "Z"
