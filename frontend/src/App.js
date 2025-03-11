import React, { useState } from "react";

const VoiceAI = () => {
    const [isRecording, setIsRecording] = useState(false);
    const [mediaRecorder, setMediaRecorder] = useState(null);
    const [audioStream, setAudioStream] = useState(null);

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            setAudioStream(stream);
            const recorder = new MediaRecorder(stream, { mimeType: "audio/webm" });

            let chunks = [];

            recorder.ondataavailable = (event) => {
                chunks.push(event.data);
            };

            recorder.onstop = async () => {
                if (chunks.length === 0) {
                    console.error("No audio recorded.");
                    return;
                }

                const audioBlob = new Blob(chunks, { type: "audio/webm" });
                sendAudioToBackend(audioBlob);
            };

            recorder.start();
            setMediaRecorder(recorder);
            setIsRecording(true);
        } catch (error) {
            console.error("Error accessing microphone:", error);
        }
    };

    const stopRecording = () => {
        if (mediaRecorder) {
            mediaRecorder.stop();
            setIsRecording(false);
            audioStream.getTracks().forEach(track => track.stop());
        }
    };

      const sendAudioToBackend = async (audioBlob) => {
        try {
            console.log("Sending audio file:", audioBlob);
            const formData = new FormData();
            formData.append("audio", audioBlob, "audio.webm"); // Add a filename
            
            const response = await fetch("http://localhost:8000/voice-ai", {
                method: "POST",
                body: formData, // fetch sets the correct Content-Type for FormData
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            // Get the audio blob from the response
            const audioData = await response.blob();
            
            // Create an audio element to play the response
            const audioUrl = URL.createObjectURL(audioData);
            const audioElement = new Audio(audioUrl);
            
            // Play the audio
            audioElement.play().catch(e => console.error("Audio playback error:", e));
            
            // Clean up the URL object when done
            audioElement.onended = () => {
                URL.revokeObjectURL(audioUrl);
            };
            
        } catch (error) {
            console.error("Error sending audio:", error);
        }
    };

    return (
        <div>
            <h1>Real-Time Voice AI</h1>
            <button onClick={isRecording ? stopRecording : startRecording}>
                {isRecording ? "Stop Recording" : "Start Recording"}
            </button>
        </div>
    );
};

export default VoiceAI;
