# OpenAI to AssemblyAI Proxy API

A FastAPI service that makes AssemblyAI's speech-to-text API compatible with the OpenAI Python SDK client. This proxy runs on Google Cloud Run and provides a seamless bridge between OpenAI's transcription API format and AssemblyAI's capabilities.

## Features

- **OpenAI-compatible API**: Drop-in replacement for OpenAI's `/v1/audio/transcriptions` endpoint
- **Direct URL support**: Accepts audio file URLs directly (no file upload required)
- **Parameter mapping**: Automatically maps OpenAI parameters to AssemblyAI equivalents
- **Error handling**: Returns OpenAI-compatible error responses
- **Production-ready**: Includes logging, health checks, and timeout handling
- **Cloud Run optimized**: Configured for Google Cloud Run deployment

## Quick Start

### Local Development

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables**:
   ```bash
   export ASSEMBLYAI_API_KEY="your-assemblyai-api-key"
   export PORT=8080
   export LOG_LEVEL=INFO
   export TIMEOUT_SECONDS=300
   ```

3. **Run the server**:
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
   ```

### Usage Example

```python
import requests

# Direct API call
response = requests.post(
    "http://localhost:8080/v1/audio/transcriptions",
    json={
        "audio_url": "https://example.com/audio.wav",
        "model": "whisper-1",
        "language": "en",
        "response_format": "json"
    }
)

transcript = response.json()
print(transcript["text"])
```

## API Reference

### POST `/v1/audio/transcriptions`

Transcribe audio from a URL using AssemblyAI's API.

**Request Body**:
```json
{
  "audio_url": "https://example.com/audio.wav",
  "model": "whisper-1",
  "language": "en",
  "prompt": "custom words to boost",
  "response_format": "json",
  "temperature": 0.0
}
```

**Parameters**:
- `audio_url` (required): URL to the audio file
- `model` (optional): Model name (ignored, but accepted for compatibility)
- `language` (optional): Language code (ISO 639-1 format)
- `prompt` (optional): Words to boost in transcription
- `response_format` (optional): "json" or "text" (default: "json")
- `temperature` (optional): Temperature setting (ignored)

**Response** (JSON format):
```json
{
  "text": "transcribed text here",
  "task": "transcribe",
  "language": "en",
  "duration": 10.5,
  "segments": [...]
}
```

### GET `/health`

Health check endpoint for monitoring and load balancers.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Parameter Mapping

| OpenAI Parameter | AssemblyAI Parameter | Notes |
|------------------|---------------------|-------|
| `audio_url` | `audio_url` | Direct mapping |
| `language` | `language_code` | ISO 639-1 format |
| `prompt` | `word_boost` | Split into array |
| `model` | - | Logged but ignored |
| `temperature` | - | Ignored |
| `response_format` | - | Controls output format |

## Environment Variables

- `ASSEMBLYAI_API_KEY` (required): Your AssemblyAI API key
- `PORT` (optional): Server port (default: 8080)
- `LOG_LEVEL` (optional): Logging level (default: INFO)
- `TIMEOUT_SECONDS` (optional): Transcription timeout (default: 300)

## Cloud Run Deployment

### Using Cloud Build

1. **Set up Cloud Build trigger**:
   ```bash
   gcloud builds triggers create github \
     --repo-name=your-repo \
     --repo-owner=your-username \
     --branch-pattern="^main$" \
     --build-config=cloudbuild.yaml
   ```

2. **Set the AssemblyAI API key**:
   ```bash
   gcloud run services update openai-assemblyai-proxy \
     --set-env-vars ASSEMBLYAI_API_KEY=your-api-key \
     --region us-central1
   ```

### Manual Deployment

1. **Build and deploy**:
   ```bash
   gcloud run deploy openai-assemblyai-proxy \
     --source . \
     --region us-central1 \
     --allow-unauthenticated \
     --memory 1Gi \
     --timeout 900 \
     --set-env-vars ASSEMBLYAI_API_KEY=your-api-key
   ```

## Error Handling

The API returns OpenAI-compatible error responses:

```json
{
  "error": {
    "message": "Error description",
    "type": "error_type",
    "code": "error_code"
  }
}
```

**Common Error Types**:
- `invalid_request_error`: Invalid parameters or audio URL
- `authentication_error`: Invalid or missing API key
- `timeout_error`: Transcription timeout
- `api_error`: AssemblyAI service errors

## Supported Audio Formats

- WAV
- MP3
- M4A
- FLAC
- OGG
- AAC
- WMA

Audio files must be accessible via public URL.

## Logging

The service provides structured logging for:
- Request/response details
- AssemblyAI API interactions
- Error conditions
- Performance metrics

## Development

### Project Structure
```
openai-assemblyai-proxy/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── assemblyai_client.py # AssemblyAI API client
│   └── utils.py             # Utility functions
├── requirements.txt         # Python dependencies
├── Dockerfile              # Container configuration
├── cloudbuild.yaml         # Cloud Build configuration
└── README.md              # This file
```

### Running Tests

```bash
# Install test dependencies
pip install pytest httpx

# Run tests (you'll need to create test files)
pytest tests/
```

## License

MIT License - see LICENSE file for details.
