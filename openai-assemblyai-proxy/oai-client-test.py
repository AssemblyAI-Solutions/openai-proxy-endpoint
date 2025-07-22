import openai
import os
import tempfile
import requests
import json
from datetime import datetime

def main():
    
    client = openai.OpenAI(
        api_key="<api-key>",
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
                response_format="json",
                prompt=json.dumps({"speaker_labels": True})  # Enable speaker labels via prompt
            )

        print(transcript)
        
        # Save JSON response to file for inspection
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"transcript_response_{timestamp}.json"
        
        # Convert transcript object to dict if needed
        transcript_dict = transcript.model_dump() if hasattr(transcript, 'model_dump') else dict(transcript)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(transcript_dict, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Response saved to: {output_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        # Clean up temporary file
        os.unlink(temp_file_path)

if __name__ == "__main__":
    main()
