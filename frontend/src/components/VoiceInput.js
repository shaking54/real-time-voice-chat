import React, { useState, useRef } from "react";

const VoiceInput = ({ onAudioSend }) => {
  const [recording, setRecording] = useState(false);
  const mediaRecorderRef = useRef(null); // Store mediaRecorder instance
  const audioChunksRef = useRef([]); // Store audio data

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
        audioChunksRef.current = []; // Clear chunks
        sendAudioToBackend(audioBlob);
      };

      mediaRecorderRef.current = mediaRecorder; // Store instance
      mediaRecorder.start();
      setRecording(true);
    } catch (error) {
      console.error("Error accessing microphone:", error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  };

  const sendAudioToBackend = async (audioBlob) => {
    const formData = new FormData();
    formData.append("audio", audioBlob);

    try {
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const audioRes = await response.blob();
        onAudioSend(audioRes);
      }
    } catch (error) {
      console.error("Error sending audio to backend:", error);
    }
  };

  return (
    <div>
      {!recording ? (
        <button onClick={startRecording}>🎙️ Start Talking</button>
      ) : (
        <button onClick={stopRecording}>⏹️ Stop</button>
      )}
    </div>
  );
};

export default VoiceInput;
