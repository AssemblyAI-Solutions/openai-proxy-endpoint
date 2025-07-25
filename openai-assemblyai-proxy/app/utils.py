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


def map_openai_model_to_speech_model(openai_model: Optional[str]) -> Optional[str]:
    """Validate and return AssemblyAI speech_model parameter"""
    if not openai_model:
        return None
    
    # Only accept valid AssemblyAI speech_model values
    valid_models = {"best", "slam-1", "universal"}
    
    if openai_model.lower() in valid_models:
        return openai_model.lower()
    
    # Return None for invalid models (will be handled by caller)
    return None


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


def parse_prompt_for_speaker_diarization(prompt: str) -> tuple[bool, str]:
    """Parse prompt for speaker diarization control and return (enabled, cleaned_prompt)"""
    if not prompt:
        return False, None
    
    # Check for speaker diarization flags (case insensitive)
    prompt_lower = prompt.lower()
    speaker_diarization = False
    
    # Look for various patterns (both speaker_labels and speaker_diarization)
    patterns = [
        "speaker_labels=true",
        "speaker_labels:true", 
        "speaker_labels true",
        "enable_speaker_labels",
        "speaker_diarization=true",
        "speaker_diarization:true", 
        "speaker_diarization true",
        "enable_speaker_diarization",
        "diarization=true",
        "diarization:true",
        "diarization true"
    ]
    
    cleaned_prompt = prompt
    for pattern in patterns:
        if pattern in prompt_lower:
            speaker_diarization = True
            # Remove the control pattern from the prompt
            # Find the actual case in the original prompt
            start_idx = prompt_lower.find(pattern)
            if start_idx != -1:
                cleaned_prompt = (prompt[:start_idx] + prompt[start_idx + len(pattern):]).strip()
            break
    
    # Return empty string as None if prompt becomes empty after cleaning
    cleaned_prompt = cleaned_prompt if cleaned_prompt else None
    
    return speaker_diarization, cleaned_prompt


def parse_prompt_for_config(prompt: str) -> tuple[dict, str]:
    """Parse prompt for AssemblyAI config parameters and return (config_dict, cleaned_prompt)"""
    if not prompt:
        return {}, None
    
    config_dict = {}
    cleaned_prompt = prompt
    
    # First, try to parse as JSON
    import json
    try:
        # Try to parse the entire prompt as JSON
        config_dict = json.loads(prompt)
        # If successful, the entire prompt was JSON config, so no cleaned prompt
        cleaned_prompt = None
        return config_dict, cleaned_prompt
    except (json.JSONDecodeError, TypeError):
        # Not valid JSON, continue with legacy pattern matching
        pass
    
    # Check for speaker diarization flags (case insensitive) - legacy support
    prompt_lower = prompt.lower()
    speaker_diarization = False
    
    # Look for various patterns (both speaker_labels and speaker_diarization)
    patterns = [
        "speaker_labels=true",
        "speaker_labels:true", 
        "speaker_labels true",
        "enable_speaker_labels",
        "speaker_diarization=true",
        "speaker_diarization:true", 
        "speaker_diarization true",
        "enable_speaker_diarization",
        "diarization=true",
        "diarization:true",
        "diarization true"
    ]
    
    for pattern in patterns:
        if pattern in prompt_lower:
            speaker_diarization = True
            config_dict["speaker_labels"] = True
            # Remove the control pattern from the prompt
            # Find the actual case in the original prompt
            start_idx = prompt_lower.find(pattern)
            if start_idx != -1:
                cleaned_prompt = (prompt[:start_idx] + prompt[start_idx + len(pattern):]).strip()
            break
    
    # Return empty string as None if prompt becomes empty after cleaning
    cleaned_prompt = cleaned_prompt if cleaned_prompt else None
    
    return config_dict, cleaned_prompt


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
    
    # Convert utterances to segments if speaker diarization is available
    if assemblyai_response.get("utterances"):
        segments = []
        for utterance in assemblyai_response["utterances"]:
            segment = {
                "id": len(segments),
                "seek": utterance.get("start", 0),
                "start": utterance.get("start", 0) / 1000.0,  # Convert ms to seconds
                "end": utterance.get("end", 0) / 1000.0,
                "text": utterance.get("text", ""),
                "speaker": utterance.get("speaker", "Unknown"),  # Add speaker info
                "tokens": [],
                "temperature": 0.0,
                "avg_logprob": 0.0,
                "compression_ratio": 1.0,
                "no_speech_prob": 0.0
            }
            segments.append(segment)
        openai_response["segments"] = segments
    # Fallback to words if no utterances (no speaker diarization)
    elif assemblyai_response.get("words"):
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
