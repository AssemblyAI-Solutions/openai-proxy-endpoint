#!/usr/bin/env python3
"""
Simple test script using OpenAI SDK with AssemblyAI proxy
"""

import openai
import requests
import tempfile
import os

def main():
    print("🧪 Simple OpenAI SDK Test with AssemblyAI Universal Model")
    print("=" * 55)
    
    # Initialize OpenAI client pointing to our proxy
    # Use your AssemblyAI API key here
    assemblyai_api_key = os.getenv("ASSEMBLYAI_API_KEY", "your-assemblyai-api-key-here")
    
    client = openai.OpenAI(
        api_key=assemblyai_api_key,  # This will be passed to AssemblyAI
        base_url="http://localhost:8080/v1"
    )
    
    # Download sample audio file
    sample_url = "https://github.com/AssemblyAI-Examples/audio-examples/raw/main/20230607_me_canadian_wildfires.mp3"
    
    print("📥 Downloading sample audio...")
    response = requests.get(sample_url, timeout=30)
    response.raise_for_status()
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        temp_file.write(response.content)
        temp_file_path = temp_file.name
    
    try:
        print("🎯 Testing transcription with 'universal' model...")
        
        # Use OpenAI SDK to transcribe with AssemblyAI universal model
        with open(temp_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="universal",  # AssemblyAI speech model
                file=audio_file,
                language="en",
                response_format="json"
            )
        
        print("✅ Success!")
        print(transcript)
        print(f"📝 Transcription: {transcript.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        # Clean up temporary file
        os.unlink(temp_file_path)

if __name__ == "__main__":
    main()
