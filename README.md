# Real-Time Voice AI Agent

## Overview
This project is a **Real-Time Voice AI Agent** that processes **live audio input**, transcribes it using **Whisper STT**, generates responses using an **LLM (Mistral via Ollama API)**, and converts the responses into speech using **Edge TTS**. The system is designed to handle real-time events and services, making it suitable for interactive AI applications.

## Architecture
The system is built with a focus on **real-time AI processing**, leveraging multiple services for speech recognition, language modeling, and text-to-speech conversion.

### Events and Services
- **Client-side Events**: Captures microphone input, sends audio streams, and plays back AI-generated speech.
- **Server-side Services**:
  - **Speech-to-Text (STT)**: Transcribes audio input using Whisper.
  - **Large Language Model (LLM)**: Processes transcriptions and generates AI-driven responses via Ollama API.
  - **Text-to-Speech (TTS)**: Converts AI-generated responses into speech using Edge TTS.
- **Streaming Pipeline**:
  - Audio is **recorded on the frontend** and streamed to the backend.
  - Backend processes audio and streams responses back in near real-time.

## System Components

### 1. **Client-Side (Frontend)**
- Built with **React**
- Uses **MediaRecorder API** to capture audio
- Streams audio data to the backend via **fetch API**
- Plays the generated speech response in real-time

### 2. **Server-Side (Backend)**
- **Flask API** with **CORS enabled**
- **Whisper STT** for transcription
- **Mistral LLM via Ollama API** for response generation
- **Edge TTS** for text-to-speech synthesis
- **Streaming response** with Flask’s `stream_with_context`

### 3. **AI Architecture**
- **Whisper STT**: Speech-to-text transcription
- **Mistral LLM**: Large language model for AI-driven responses. Using Ollama API for response generation. Host the model on Google Colab T4 and expose it via ngrok tunnelling.
- **Edge TTS**: Text-to-speech synthesis for generating speech responses.

## Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js & npm (for frontend)
- ffmpeg (for audio processing)
- Dependencies: Flask, requests, whisper, numpy, edge_tts, pydub

### Backend Setup
```sh
pip install -r requirements.txt
python app.py
```

### Frontend Setup
```sh
cd frontend
npm install
npm run dev
```

## Usage
1. Start the backend server (`app.py`)
2. Start the frontend (`npm start`)
3. Click the **record button** to speak
4. The system will transcribe, process, and respond in real-time

## API Endpoints
### `/voice-ai` (POST)
- **Input**: Audio stream (WebM/WAV format)
- **Output**: Streamed AI-generated speech response

## Troubleshooting
- **No audio received?** Ensure your browser has microphone permissions enabled.
- **Audio format error?** Convert input to WAV format using `pydub`.
- **CORS issue?** Ensure CORS is enabled in Flask.

## Future Enhancements
- **Support for multiple voices & languages**
- **WebSocket implementation for low-latency interaction**
- **Enhanced error handling & logging**

## License
MIT License

