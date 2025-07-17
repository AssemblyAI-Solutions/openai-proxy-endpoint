from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from enum import Enum


class ResponseFormat(str, Enum):
    JSON = "json"
    TEXT = "text"


class OpenAITranscriptionRequest(BaseModel):
    audio_url: str = Field(..., description="URL to the audio file")
    model: Optional[str] = Field(default="whisper-1", description="Model to use (ignored)")
    language: Optional[str] = Field(default=None, description="Language code (ISO 639-1)")
    prompt: Optional[str] = Field(default=None, description="Prompt for word boost")
    response_format: Optional[ResponseFormat] = Field(default=ResponseFormat.JSON, description="Response format")
    temperature: Optional[float] = Field(default=0.0, description="Temperature (ignored)")


class OpenAITranscriptionResponse(BaseModel):
    text: str
    task: str = "transcribe"
    language: Optional[str] = None
    duration: Optional[float] = None
    segments: Optional[List[Dict[str, Any]]] = None


class AssemblyAITranscriptionRequest(BaseModel):
    audio_url: str
    language_code: Optional[str] = None
    word_boost: Optional[List[str]] = None
    speech_model: Optional[str] = None
    punctuate: bool = True
    format_text: bool = True


class AssemblyAITranscriptionResponse(BaseModel):
    id: str
    status: str
    text: Optional[str] = None
    audio_duration: Optional[float] = None
    language_code: Optional[str] = None
    confidence: Optional[float] = None
    words: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None


class ErrorResponse(BaseModel):
    error: Dict[str, Any]


class HealthResponse(BaseModel):
    status: str = "healthy"
    timestamp: str
