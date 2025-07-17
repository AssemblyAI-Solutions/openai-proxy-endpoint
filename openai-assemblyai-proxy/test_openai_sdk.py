#!/usr/bin/env python3
"""
Test script using OpenAI SDK to verify the proxy API works correctly
"""

import os
import requests
import json
import tempfile
import openai
from typing import Optional


def test_with_openai_sdk_file_upload():
    """Test using actual OpenAI SDK with file upload"""
    print("Testing with OpenAI SDK (file upload)...")
    
    base_url = os.getenv("API_BASE_URL", "http://localhost:8080")
    
    # Initialize OpenAI client with our proxy
    client = openai.OpenAI(
        api_key="dummy-key",  # Not used by our proxy
        base_url=f"{base_url}/v1"
    )
    
    # Download a sample audio file to test with
    sample_url = "https://github.com/AssemblyAI-Examples/audio-examples/raw/main/20230607_me_canadian_wildfires.mp3"
    
    try:
        print(f"Downloading sample audio file...")
        response = requests.get(sample_url, timeout=30)
        response.raise_for_status()
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_file.write(response.content)
            temp_file_path = temp_file.name
        
        print(f"Testing transcription with OpenAI SDK...")
        
        # Use OpenAI SDK to transcribe
        with open(temp_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="en",
                response_format="json"
            )
        
        print("✅ Success! OpenAI SDK transcription completed")
        print(f"Text: {transcript.text[:200]}..." if len(transcript.text) > 200 else f"Text: {transcript.text}")
        
        # Clean up
        os.unlink(temp_file_path)
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI SDK test failed: {str(e)}")
        # Clean up on error
        try:
            os.unlink(temp_file_path)
        except:
            pass
        return False


def test_with_openai_sdk_url_fallback():
    """Test using requests to simulate OpenAI SDK with URL parameter"""
    print("Testing with URL parameter (fallback method)...")
    
    base_url = os.getenv("API_BASE_URL", "http://localhost:8080")
    
    # Sample audio URL
    audio_url = "https://github.com/AssemblyAI-Examples/audio-examples/raw/main/20230607_me_canadian_wildfires.mp3"
    
    # Use form data to match our API
    form_data = {
        "audio_url": audio_url,
        "model": "whisper-1",
        "language": "en",
        "response_format": "json"
    }
    
    try:
        print(f"Making request to: {base_url}/v1/audio/transcriptions")
        print(f"Form data: {json.dumps(form_data, indent=2)}")
        
        response = requests.post(
            f"{base_url}/v1/audio/transcriptions",
            data=form_data,
            timeout=120
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! URL fallback test completed")
            text = data.get('text', '')
            print(f"Text: {text[:200]}..." if len(text) > 200 else f"Text: {text}")
            return True
        else:
            print("❌ Failed! Error response:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
        return False


def check_server_health():
    """Check if the server is running"""
    base_url = os.getenv("API_BASE_URL", "http://localhost:8080")
    
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server is healthy: {data.get('status')}")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {str(e)}")
        print("Make sure the server is running with: python -m uvicorn app.main:app --reload")
        return False





def main():
    """Main test function"""
    print("🧪 Testing OpenAI to AssemblyAI Proxy API with OpenAI SDK")
    print("=" * 60)
    
    # Check environment
    if not os.getenv("ASSEMBLYAI_API_KEY"):
        print("⚠️  Warning: ASSEMBLYAI_API_KEY not set")
        print("   Set it with: export ASSEMBLYAI_API_KEY='your-key-here'")
        print()
    
    # Check server health first
    if not check_server_health():
        return 1
    
    print()
    
    # Run tests
    success_count = 0
    total_tests = 2
    
    # Test 1: OpenAI SDK with file upload
    print("Test 1: OpenAI SDK with file upload")
    print("-" * 40)
    if test_with_openai_sdk_file_upload():
        success_count += 1
    print()
    
    # Test 2: URL fallback method
    print("Test 2: URL parameter fallback")
    print("-" * 40)
    if test_with_openai_sdk_url_fallback():
        success_count += 1
    print()
    
    print("=" * 60)
    print(f"🎯 Test Summary: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All tests passed!")
        print("\n💡 Your proxy API is working correctly with the OpenAI SDK!")
        print("   You can now use it as a drop-in replacement for OpenAI's transcription API")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    exit(main())
