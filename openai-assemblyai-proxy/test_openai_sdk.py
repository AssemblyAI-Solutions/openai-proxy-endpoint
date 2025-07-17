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
                model="best",  # Use valid AssemblyAI model
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


def test_assemblyai_speech_models():
    """Test different AssemblyAI speech models using OpenAI SDK"""
    base_url = os.getenv("API_BASE_URL", "http://localhost:8080")
    
    # Initialize OpenAI client with our proxy
    client = openai.OpenAI(
        api_key="dummy-key",  # Not used by our proxy
        base_url=f"{base_url}/v1"
    )
    
    # Test different AssemblyAI speech models
    models_to_test = ["best", "slam-1", "universal"]
    sample_url = "https://github.com/AssemblyAI-Examples/audio-examples/raw/main/20230607_me_canadian_wildfires.mp3"
    
    results = []
    
    for model in models_to_test:
        print(f"Testing AssemblyAI speech model: {model}")
        
        try:
            # Download sample audio file
            response = requests.get(sample_url, timeout=30)
            response.raise_for_status()
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                temp_file.write(response.content)
                temp_file_path = temp_file.name
            
            # Use OpenAI SDK to transcribe with specific model
            with open(temp_file_path, "rb") as audio_file:
                transcript = client.audio.transcriptions.create(
                    model=model,  # Use AssemblyAI speech model
                    file=audio_file,
                    language="en",
                    response_format="json"
                )
            
            print(f"✅ Success with model '{model}'!")
            print(f"Text: {transcript.text[:100]}..." if len(transcript.text) > 100 else f"Text: {transcript.text}")
            results.append((model, True, None))
            
            # Clean up
            os.unlink(temp_file_path)
            
        except Exception as e:
            print(f"❌ Failed with model '{model}': {str(e)}")
            results.append((model, False, str(e)))
            # Clean up on error
            try:
                os.unlink(temp_file_path)
            except:
                pass
        
        print()
    
    return results


def test_invalid_model_rejection():
    """Test that invalid models (like whisper-1) are properly rejected"""
    print("Testing invalid model rejection...")
    
    base_url = os.getenv("API_BASE_URL", "http://localhost:8080")
    
    # Initialize OpenAI client with our proxy
    client = openai.OpenAI(
        api_key="dummy-key",  # Not used by our proxy
        base_url=f"{base_url}/v1"
    )
    
    sample_url = "https://github.com/AssemblyAI-Examples/audio-examples/raw/main/20230607_me_canadian_wildfires.mp3"
    
    try:
        # Download sample audio file
        response = requests.get(sample_url, timeout=30)
        response.raise_for_status()
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_file.write(response.content)
            temp_file_path = temp_file.name
        
        # Try to use invalid model (should fail)
        with open(temp_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",  # Invalid model
                file=audio_file,
                language="en",
                response_format="json"
            )
        
        # If we get here, the test failed (should have thrown an error)
        print("❌ FAIL: Invalid model was accepted (should have been rejected)")
        os.unlink(temp_file_path)
        return False
        
    except Exception as e:
        error_msg = str(e)
        if "invalid_model" in error_msg.lower() or "invalid model" in error_msg.lower():
            print(f"✅ SUCCESS: Invalid model properly rejected")
            print(f"Error message: {error_msg}")
            # Clean up
            try:
                os.unlink(temp_file_path)
            except:
                pass
            return True
        else:
            print(f"❌ FAIL: Unexpected error: {error_msg}")
            # Clean up
            try:
                os.unlink(temp_file_path)
            except:
                pass
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
    total_tests = 3
    
    # Test 1: OpenAI SDK with file upload (default model)
    print("Test 1: OpenAI SDK with file upload (default model)")
    print("-" * 50)
    if test_with_openai_sdk_file_upload():
        success_count += 1
    print()
    
    # Test 2: AssemblyAI speech models
    print("Test 2: AssemblyAI speech models (best, slam-1, universal)")
    print("-" * 60)
    model_results = test_assemblyai_speech_models()
    successful_models = sum(1 for _, success, _ in model_results if success)
    if successful_models == len(model_results):
        success_count += 1
        print(f"✅ All {len(model_results)} AssemblyAI speech models work correctly!")
    else:
        print(f"❌ Only {successful_models}/{len(model_results)} models worked")
    print()
    
    # Test 3: Invalid model rejection
    print("Test 3: Invalid model rejection (whisper-1 should be rejected)")
    print("-" * 65)
    if test_invalid_model_rejection():
        success_count += 1
    print()
    
    print("=" * 60)
    print(f"🎯 Test Summary: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All tests passed!")
        print("\n💡 Your proxy API is working correctly with the OpenAI SDK!")
        print("   - Supports AssemblyAI speech models: 'best', 'slam-1', 'universal'")
        print("   - Properly rejects invalid models like 'whisper-1'")
        print("   - Works as a drop-in replacement for OpenAI's transcription API")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    exit(main())
