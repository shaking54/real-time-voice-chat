import whisper

model = whisper.load_model("tiny")

def transcribe_audio(audio_path):
    try:
        result = model.transcribe(audio_path, fp16=False)
        return result['text']
    except Exception as e:
        print(f"Error in STT: {e}")
        return None
