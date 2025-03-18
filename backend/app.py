from flask import Flask, request, Response, stream_with_context
from flask_cors import CORS
import json
import requests
import whisper
import edge_tts
import asyncio

from pydub import AudioSegment
from io import BytesIO
import os

import torch

import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
# CORS(app)  # Enable CORS for all routes

device = "cuda" if torch.cuda.is_available() else "cpu"
# Load models
stt_model = whisper.load_model("tiny")

# OLLAMA API URL
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL")

# TTS Voice Selection
VOICE = "en-GB-SoniaNeural"


def convert_webm_to_wav(webm_data):
    """Convert WebM audio data to WAV format."""
    try:
        audio = AudioSegment.from_file(BytesIO(webm_data), format="webm")
        wav_io = BytesIO()
        audio.export(wav_io, format="wav")
        return wav_io.getvalue()
    except Exception as e:
        print(f"🚨 Error converting WebM to WAV: {e}")
        return None


def transcribe_stream(audio_path):
    """Convert audio to text using Whisper STT."""
    if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
        raise ValueError("Received empty audio data")

    try:
        result = stt_model.transcribe(audio_path, fp16=False)
        return result["text"]
    except Exception as e:
        print(f"🚨 Error during transcription: {e}")
        return "Error in transcription"


def stream_llm_response(prompt):
    """Stream LLM response from an external API."""
    path = "api/generate"
    response = requests.post(
        os.path.join(OLLAMA_API_URL, path), json={"model": "mistral", "prompt": prompt}, stream=True
    )
    for chunk in response.iter_lines():
        if chunk:
            try:
                chunk_data = json.loads(chunk.decode("utf-8"))
                if "response" in chunk_data:
                    yield chunk_data["response"]
            except json.JSONDecodeError:
                continue


async def text_to_speech(text):
    """Convert text to speech using Edge TTS."""
    if not text or not text.strip():
        print("🚨 Skipping empty text for TTS")
        return b""
    
    try:
        print(f"🔊 Sending to TTS: '{text}'")
        communicate = edge_tts.Communicate(text, VOICE)
        audio_data = b""
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
                
        return audio_data
    except Exception as e:
        print(f"🚨 TTS Error: {e}")
        return b""


def generate_response(text):
    """Stream LLM response and convert to speech in real-time."""
    
    def generate():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        buffer = ""
        
        # Stream the LLM response and process each chunk
        for llm_chunk in stream_llm_response(text):
            buffer += llm_chunk
            
            # Process complete sentences or when buffer gets large enough
            if buffer.endswith(('.', '!', '?', ':', '\n', ",")):
                try:
                    audio_data = loop.run_until_complete(text_to_speech(buffer))
                    if audio_data:
                        # Send this chunk immediately to frontend
                        yield audio_data
                    buffer = ""
                except Exception as e:
                    print(f"🚨 Error processing chunk: {e}")
        
        # Process any remaining text
        if buffer.strip():
            try:
                audio_data = loop.run_until_complete(text_to_speech(buffer))
                if audio_data:
                    yield audio_data
            except Exception as e:
                print(f"🚨 Error processing final chunk: {e}")
        
        loop.close()
    
    # Important: Use chunked transfer encoding
    return Response(
        generate(), 
        mimetype="audio/wav"
    )


@app.route("/voice-ai", methods=["POST"])
def voice_ai():
    """Main endpoint for voice AI processing."""
    if "audio" not in request.files:
        return "No audio file provided", 400

    audio_file = request.files["audio"]
    if audio_file.filename.endswith(".webm"):
        webm_data = audio_file.read()
        wav_data = convert_webm_to_wav(webm_data)
        if not wav_data:
            return "Failed to process audio", 400
        audio_path = "/tmp/audio.wav"
        with open(audio_path, "wb") as f:
            f.write(wav_data)
    else:
        audio_path = os.path.join("/tmp", audio_file.filename)
        audio_file.save(audio_path)

    text = transcribe_stream(audio_path)
    print(f"Transcribed Text: {text}")

    return generate_response(text)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)