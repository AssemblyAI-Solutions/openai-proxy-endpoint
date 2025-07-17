#!/usr/bin/env python3
"""
Simple test script for the OpenAI to AssemblyAI Proxy API
"""

import requests
import json
import os
import time


def test_health_endpoint(base_url):
    """Test the health check endpoint"""
    print("Testing health endpoint...")
    
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Health check passed: {data['status']}")
        return True
        
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return False


def test_transcription_endpoint(base_url, audio_url):
    """Test the transcription endpoint"""
    print(f"Testing transcription endpoint with audio URL: {audio_url}")
    
    payload = {
        "audio_url": audio_url,
        "model": "whisper-1",
        "language": "en",
        "response_format": "json"
    }
    
    try:
        print("Sending transcription request...")
        response = requests.post(
            f"{base_url}/v1/audio/transcriptions",
            json=payload,
            timeout=120  # Allow time for transcription
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Transcription successful!")
            print(f"Text: {data.get('text', 'No text returned')}")
            print(f"Language: {data.get('language', 'Unknown')}")
            print(f"Duration: {data.get('duration', 'Unknown')} seconds")
            return True
        else:
            print(f"❌ Transcription failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Transcription request failed: {str(e)}")
        return False


def test_error_handling(base_url):
    """Test error handling with invalid audio URL"""
    print("Testing error handling...")
    
    payload = {
        "audio_url": "https://invalid-url.com/nonexistent.wav",
        "model": "whisper-1"
    }
    
    try:
        response = requests.post(
            f"{base_url}/v1/audio/transcriptions",
            json=payload,
            timeout=30
        )
        
        if response.status_code >= 400:
            print("✅ Error handling working correctly")
            try:
                error_data = response.json()
                print(f"Error response: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error response: {response.text}")
            return True
        else:
            print("❌ Expected error but got success response")
            return False
            
    except Exception as e:
        print(f"❌ Error handling test failed: {str(e)}")
        return False


def main():
    """Main test function"""
    # Configuration
    base_url = os.getenv("API_BASE_URL", "http://localhost:8080")
    
    # Sample audio URL (you can replace with your own)
    audio_url = "https://github.com/AssemblyAI-Examples/audio-examples/raw/main/20230607_me_canadian_wildfires.mp3"
    
    print(f"Testing OpenAI to AssemblyAI Proxy API at: {base_url}")
    print("=" * 60)
    
    # Check if AssemblyAI API key is set
    if not os.getenv("ASSEMBLYAI_API_KEY"):
        print("⚠️  Warning: ASSEMBLYAI_API_KEY not set in environment")
        print("   The transcription test will likely fail")
        print()
    
    # Run tests
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Health check
    if test_health_endpoint(base_url):
        tests_passed += 1
    print()
    
    # Test 2: Transcription
    if test_transcription_endpoint(base_url, audio_url):
        tests_passed += 1
    print()
    
    # Test 3: Error handling
    if test_error_handling(base_url):
        tests_passed += 1
    print()
    
    # Summary
    print("=" * 60)
    print(f"Tests completed: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    exit(main())
