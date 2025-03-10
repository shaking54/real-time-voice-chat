import requests
import os
from TTS.api import TTS
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
model = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=True).to(device)

output_dir = "/tmp/"

def synthesize_speech(text):
    try:
        audio_path = os.path.join(output_dir, "response.wav")
        model.tts_to_file(text=text, file_path=audio_path)
        return audio_path

    except Exception as e:
        print(f"Error in TTS: {e}")
        return None

if __name__ == '__main__':
    text = 'Can you describe the weather today?'
    synthesize_speech(text)
    import os
import requests


OLLAMA_API_URL = os.getenv("OLLAMA_API_URL")

def fake_generate_response(prompt):
    return prompt

def generate_response(prompt):
    
    try:
        response = requests.post(OLLAMA_API_URL, json={'model': 'mistral', 'prompt': prompt})
        response_data = response.json()
        return response_data.get('response', None)
    except Exception as e:
        print(f"Error in LLM: {e}")
        return None
