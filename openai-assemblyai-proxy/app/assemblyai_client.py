import requests
import time
import os
import logging
from typing import Dict, Any, Optional
from .models import AssemblyAITranscriptionRequest, AssemblyAITranscriptionResponse
from .utils import format_openai_error


class AssemblyAIClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ASSEMBLYAI_API_KEY")
        if not self.api_key:
            raise ValueError("AssemblyAI API key is required")
        
        self.base_url = "https://api.assemblyai.com/v2"
        self.headers = {
            "authorization": self.api_key,
            "content-type": "application/json"
        }
        self.logger = logging.getLogger(__name__)
        
        # Timeout and polling settings
        self.timeout_seconds = 300
        self.poll_interval = 0.1 #100ms polling interval
        self.upload_url = f"{self.base_url}/upload"
    
    def upload_file(self, file_content: bytes, filename: str) -> str:
        """Upload file to AssemblyAI and return the upload URL"""
        self.logger.info(f"Uploading file: {filename}")
        
        try:
            response = requests.post(
                self.upload_url,
                files={'file': (filename, file_content)},
                headers={'authorization': self.api_key},
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            upload_url = result.get('upload_url')
            
            if not upload_url:
                raise Exception("No upload URL returned from AssemblyAI")
            
            self.logger.info(f"File uploaded successfully: {upload_url}")
            return upload_url
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to upload file: {str(e)}")
            raise Exception(f"Failed to upload file: {str(e)}")
    
    def submit_transcription(self, request: AssemblyAITranscriptionRequest) -> Dict[str, Any]:
        """Submit transcription job to AssemblyAI"""
        url = f"{self.base_url}/transcript"
        
        payload = {
            "audio_url": request.audio_url,
            "punctuate": request.punctuate,
            "format_text": request.format_text
        }
        
        if request.language_code:
            payload["language_code"] = request.language_code
        
        if request.word_boost:
            payload["word_boost"] = request.word_boost
        
        if request.speech_model:
            payload["speech_model"] = request.speech_model
        
        if request.speaker_labels is not None:
            payload["speaker_labels"] = request.speaker_labels
        
        self.logger.info(f"Submitting transcription job for audio URL: {request.audio_url}")
        self.logger.info(f"Payload being sent to AssemblyAI: {payload}")
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            self.logger.info(f"Transcription job submitted successfully: {result.get('id')}")
            return result
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to submit transcription job: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    self.logger.error(f"AssemblyAI error response: {error_detail}")
                except:
                    self.logger.error(f"AssemblyAI response text: {e.response.text}")
            raise Exception(f"Failed to submit transcription job: {str(e)}")
    
    def get_transcription_status(self, transcript_id: str) -> Dict[str, Any]:
        """Get transcription status from AssemblyAI"""
        url = f"{self.base_url}/transcript/{transcript_id}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to get transcription status: {str(e)}")
            raise Exception(f"Failed to get transcription status: {str(e)}")
    
    def wait_for_completion(self, transcript_id: str) -> Dict[str, Any]:
        """Poll for transcription completion with fixed 100ms interval"""
        start_time = time.time()
        
        self.logger.info(f"Waiting for transcription completion: {transcript_id}")
        
        while time.time() - start_time < self.timeout_seconds:
            try:
                result = self.get_transcription_status(transcript_id)
                status = result.get("status")
                
                self.logger.debug(f"Transcription status: {status}")
                
                if status == "completed":
                    self.logger.info(f"Transcription completed successfully: {transcript_id}")
                    return result
                elif status == "error":
                    error_msg = result.get("error", "Unknown error occurred")
                    self.logger.error(f"Transcription failed: {error_msg}")
                    raise Exception(f"Transcription failed: {error_msg}")
                elif status in ["queued", "processing"]:
                    # Continue polling with fixed interval
                    time.sleep(self.poll_interval)
                else:
                    self.logger.warning(f"Unknown status: {status}")
                    time.sleep(self.poll_interval)
                    
            except Exception as e:
                if "Transcription failed:" in str(e):
                    raise  # Re-raise transcription errors
                
                self.logger.warning(f"Error polling status, retrying: {str(e)}")
                time.sleep(self.poll_interval)
        
        # Timeout reached
        self.logger.error(f"Transcription timeout after {self.timeout_seconds} seconds")
        raise Exception(f"Transcription timeout after {self.timeout_seconds} seconds")
    
    def transcribe(self, request: AssemblyAITranscriptionRequest) -> Dict[str, Any]:
        """Complete transcription workflow"""
        try:
            # Submit transcription job
            submit_result = self.submit_transcription(request)
            transcript_id = submit_result.get("id")
            
            if not transcript_id:
                raise Exception("No transcript ID returned from AssemblyAI")
            
            # Wait for completion
            result = self.wait_for_completion(transcript_id)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Transcription workflow failed: {str(e)}")
            raise
