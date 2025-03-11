import requests
import os
from TTS.api import TTS
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
model = TTS(model_name="tts_models/en/ljspeech/fast_pitch", progress_bar=True).to(device)

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