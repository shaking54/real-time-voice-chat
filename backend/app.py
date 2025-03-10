from flask import Flask, request, jsonify, send_file
from stt import transcribe_audio
from llm import generate_response, fake_generate_response
from tts import synthesize_speech
from flask_cors import CORS  # Import CORS
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/chat', methods=['POST'])
def chat():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    audio_path = os.path.join('/tmp', audio_file.filename)
    audio_file.save(audio_path)

    # Speech-to-Text
    text = transcribe_audio(audio_path)
    if text is None:
        return jsonify({'error': 'STT failed'}), 500

    # Generate Response
    response_text = generate_response(text)
    if response_text is None:
        return jsonify({'error': 'LLM failed'}), 500

    # Text-to-Speech
    audio_response_path = synthesize_speech(response_text)
    if audio_response_path is None:
        return jsonify({'error': 'TTS failed'}), 500

    return send_file(audio_response_path, mimetype='audio/wav')

@app.route('/test', methods=['GET'])
def test():
    return send_file("./input.wav", mimetype='audio/wav')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
