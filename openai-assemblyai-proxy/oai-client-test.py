import openai
import requests
import tempfile
import os

def main():
    
    client = openai.OpenAI(
        api_key="your-assemblyai-api-key-here",  # This will be passed to AssemblyAI
        base_url="https://assemblyai-oai-client-142150461292.us-west1.run.app/v1"
    )
    
    # Download sample audio file
    sample_url = "https://github.com/AssemblyAI-Examples/audio-examples/raw/main/20230607_me_canadian_wildfires.mp3"
    
    response = requests.get(sample_url, timeout=30)
    response.raise_for_status()
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        temp_file.write(response.content)
        temp_file_path = temp_file.name
    
    try:
        with open(temp_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="universal",  # AssemblyAI speech model
                file=audio_file,
                language="en",
                response_format="json"
            )

        print(transcript)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        # Clean up temporary file
        os.unlink(temp_file_path)

if __name__ == "__main__":
    main()
