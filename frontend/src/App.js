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
            
            // Create a response for streaming audio
            const response = await fetch("http://localhost:8000/voice-ai", {
                method: "POST",
                body: formData,
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            // Set up a readable stream from the response
            const reader = response.body.getReader();
            let chunks = [];
            
            // Function to process the incoming chunks
            async function processChunks() {
                while (true) {
                    const { done, value } = await reader.read();
                    
                    if (done) {
                        console.log("Stream complete");
                        break;
                    }
                    
                    // Process the chunk (value is a Uint8Array)
                    if (value && value.length > 0) {
                        console.log(`Received audio chunk: ${value.length} bytes`);
                        
                        // Create a blob from this chunk
                        const chunk = new Blob([value], { type: 'audio/wav' });
                        chunks.push(chunk);
                        
                        // Play this chunk immediately
                        const audioUrl = URL.createObjectURL(chunk);
                        const audioElement = new Audio(audioUrl);
                        
                        // Wait for the audio to finish playing before cleaning up
                        audioElement.onended = () => {
                            URL.revokeObjectURL(audioUrl);
                        };
                        
                        // Play the audio
                        try {
                            await audioElement.play();
                        } catch (e) {
                            console.error("Failed to play audio chunk:", e);
                        }
                    }
                }
            }
            
            // Start processing chunks
            await processChunks();
            
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
