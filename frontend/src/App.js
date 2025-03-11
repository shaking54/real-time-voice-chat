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
            formData.append("audio", audioBlob, "audio.webm");
    
            // Send request to backend
            const response = await fetch("http://localhost:8000/voice-ai", {
                method: "POST",
                body: formData,
            });
    
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
    
            // Read streaming response
            const reader = response.body.getReader();
            let chunks = [];
    
            async function processChunksSequentially() {
                let audioElement = null;
    
                while (true) {
                    const { done, value } = await reader.read();
                    if (done) {
                        console.log("Stream complete");
                        break;
                    }
    
                    if (value && value.length > 0) {
                        console.log(`Received audio chunk: ${value.length} bytes`);
    
                        // Create a blob from this chunk
                        const chunk = new Blob([value], { type: "audio/wav" });
                        chunks.push(chunk);
    
                        // Generate URL for the audio chunk
                        const audioUrl = URL.createObjectURL(chunk);
    
                        // Wait for previous audio to finish before playing new one
                        if (audioElement) {
                            await new Promise(resolve => audioElement.onended = resolve);
                        }
    
                        // Play the new chunk
                        audioElement = new Audio(audioUrl);
                        try {
                            await audioElement.play(); // Ensure playback starts before proceeding
                        } catch (e) {
                            console.error("Playback error:", e);
                        }
    
                        // Cleanup URL after playback
                        audioElement.onended = () => {
                            URL.revokeObjectURL(audioUrl);
                        };
                    }
                }
            }
    
            // Start processing chunks sequentially
            await processChunksSequentially();
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
