# from flask import Flask, request, Response, stream_with_context
# from flask_cors import CORS
# import json
# import requests
# import whisper
# import numpy as np
# import edge_tts
# import asyncio

# from pydub import AudioSegment
# from io import BytesIO

# import os

# app = Flask(__name__)
# CORS(app)  # Enable CORS for all routes

# # Load models
# stt_model = whisper.load_model("base")

# # OLLAMA API URL
# OLLAMA_API_URL = "https://d1a7-35-204-235-12.ngrok-free.app/api/generate"

# # TTS Voice Selection
# VOICE = "en-GB-SoniaNeural"


# def convert_webm_to_wav(webm_data):
#     audio = AudioSegment.from_file(BytesIO(webm_data), format="webm")
#     wav_io = BytesIO()
#     audio.export(wav_io, format="wav")
#     return wav_io.getvalue()

# def transcribe_stream(audio_path):
#     """Convert raw audio to text using Whisper STT."""
#     if not audio_path:
#         raise ValueError("Received empty audio data")
    
#     try:
#         # Transcribe using Whisper
#         result = stt_model.transcribe(audio_path, fp16=False)
#         return result["text"]

#     except Exception as e:
#         print(f"Error during transcription: {e}")
#         return "Error in transcription"

# def stream_llm_response(prompt):
#     """Stream LLM response from external API."""
#     response = requests.post(OLLAMA_API_URL, json={'model': 'mistral', 'prompt': prompt}, stream=True)
#     for chunk in response.iter_lines():
#         if chunk:
#             try:
#                 chunk_data = json.loads(chunk.decode("utf-8"))
#                 # print("LLM Response:", chunk_data)  # ✅ Debugging
#                 yield chunk_data["response"]
#             except json.JSONDecodeError:
#                 continue

# async def stream_tts_async(text):
#     """Async generator to stream TTS audio chunks."""
#     print(text)
#     communicate = edge_tts.Communicate(text, VOICE)
#     async for chunk in communicate.stream():
#         if chunk["type"] == "audio":
#             yield chunk["data"]

# def stream_tts(text):
#     """Run async TTS in a sync function and yield chunks."""
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     return loop.run_until_complete(_gather_tts_chunks(text))

# async def _gather_tts_chunks(text):
#     """Gather all async TTS chunks into a list (workaround for asyncio limitations)."""
#     chunks = []
#     async for chunk in stream_tts_async(text):
#         chunks.append(chunk)
#     return chunks  # Returning a list of audio chunks

# @app.route("/voice-ai", methods=["POST"])
# def voice_ai():
#     """Main endpoint for voice AI processing."""
    
#     audio_file = request.files['audio']
#     audio_path = os.path.join('/tmp', audio_file.filename)
#     audio_file.save(audio_path)
#     text = transcribe_stream(audio_path)
#     print(text)
#     def generate_response():
#         """Stream LLM response and convert to speech in real-time."""
#         for llm_chunk in stream_llm_response(text):
#             yield llm_chunk.encode("utf-8")  # Stream LLM text response
#             for tts_chunk in stream_tts(llm_chunk):  # Convert LLM response to speech
#                 yield tts_chunk
#     return Response(stream_with_context(generate_response()), mimetype="audio/wav")

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000)

from flask import Flask, request, Response
from flask_cors import CORS
import json
import requests
import whisper
import edge_tts
import asyncio

from pydub import AudioSegment
from io import BytesIO
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load models
stt_model = whisper.load_model("base")

# OLLAMA API URL
OLLAMA_API_URL = "https://d1a7-35-204-235-12.ngrok-free.app/api/generate"

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
    response = requests.post(
        OLLAMA_API_URL, json={"model": "mistral", "prompt": prompt}, stream=True
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
        # Make sure we have a complete sentence to avoid the NoAudioReceived error
        if not text.endswith(('.', '!', '?', ',', ':', ';')):
            text = text + "."
            
        # Ensure minimum text length
        if len(text.strip()) < 3:
            text = text + " Yes."
            
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


def process_llm_chunks(text_chunks):
    """Process LLM response chunks, combining them sensibly for TTS."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    buffer = ""
    audio_chunks = []
    
    for chunk in text_chunks:
        buffer += chunk
        
        # Process complete sentences or when buffer gets large enough
        if buffer.endswith(('.', '!', '?')) or len(buffer) > 50:
            try:
                audio_data = loop.run_until_complete(text_to_speech(buffer))
                if audio_data:
                    audio_chunks.append(audio_data)
                buffer = ""
            except Exception as e:
                print(f"🚨 Error processing chunk: {e}")
    
    # Process any remaining text
    if buffer.strip():
        try:
            audio_data = loop.run_until_complete(text_to_speech(buffer))
            if audio_data:
                audio_chunks.append(audio_data)
        except Exception as e:
            print(f"🚨 Error processing final chunk: {e}")
    
    loop.close()
    return audio_chunks


def generate_response(text):
    """Stream LLM response and convert to speech in real-time."""
    
    def generate():
        # Get the LLM response text chunks
        text_chunks = list(stream_llm_response(text))
        
        # Get processed audio chunks
        audio_chunks = process_llm_chunks(text_chunks)
        
        # Stream the audio chunks
        for chunk in audio_chunks:
            yield chunk
    
    return Response(generate(), mimetype="audio/wav")


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
    print(f"📝 Transcribed Text: {text}")

    return generate_response(text)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)