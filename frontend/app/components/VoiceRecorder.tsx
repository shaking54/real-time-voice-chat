"use client";

import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Mic, StopCircle } from "lucide-react";

export default function VoiceRecorder() {
  const [isRecording, setIsRecording] = useState(false);
  const [processingTime, setProcessingTime] = useState<number | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioStreamRef = useRef<MediaStream | null>(null);
  const requestStartTimeRef = useRef<number | null>(null);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioStreamRef.current = stream;
      const recorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
      let chunks: BlobPart[] = [];

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
      mediaRecorderRef.current = recorder;
      setIsRecording(true);
      setProcessingTime(null); // Reset processing time
    } catch (error) {
      console.error("Error accessing microphone:", error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);

      if (audioStreamRef.current) {
        audioStreamRef.current.getTracks().forEach(track => track.stop());
        audioStreamRef.current = null;
      }

      mediaRecorderRef.current = null;
    } else {
      console.error("No active recorder found.");
    }
  };

  const sendAudioToBackend = async (audioBlob: Blob) => {
    try {
      console.log("Sending audio file:", audioBlob);
      const formData = new FormData();
      formData.append("audio", audioBlob, "audio.webm");

      // Record the start time
      requestStartTimeRef.current = performance.now();
      console.log("Request start time:", requestStartTimeRef.current);

      const response = await fetch("http://localhost:8000/voice-ai", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      if (!response.body) {
        throw new Error("Response body is null.");
      }

      const reader = response.body.getReader();
      let chunks: Blob[] = [];
      let firstChunkReceived = false;

      async function processChunksSequentially() {
        let audioElement: HTMLAudioElement | null = null;

        while (true) {
          const { done, value } = await reader.read();
          if (done) {
            console.log("Stream complete");
            break;
          }

          if (value && value.length > 0) {
            console.log(`Received audio chunk: ${value.length} bytes`);
            const chunk = new Blob([value], { type: "audio/wav" });
            chunks.push(chunk);
            const audioUrl = URL.createObjectURL(chunk);

            if (!firstChunkReceived && requestStartTimeRef.current) {
              const firstChunkTime = performance.now();
              const processingTimeMs = firstChunkTime - requestStartTimeRef.current;
              setProcessingTime(processingTimeMs);
              console.log("First chunk received time:", firstChunkTime);
              console.log("Processing time (ms):", processingTimeMs);
              firstChunkReceived = true;
            }

            if (audioElement) {
              await new Promise(resolve => (audioElement!.onended = resolve));
            }

            audioElement = new Audio(audioUrl);
            
            try {
              const playPromise = audioElement.play();
              
              // Capture the first audio playback time
              if (firstChunkReceived && playPromise && requestStartTimeRef.current) {
                playPromise.then(() => {
                  if (audioElement?.currentTime === 0 && requestStartTimeRef.current) {
                    const playbackStartTime = performance.now();
                    const totalTimeToAudio = playbackStartTime - requestStartTimeRef.current;
                    console.log("First audio playback time:", playbackStartTime);
                    console.log("Total time to first audio (ms):", totalTimeToAudio);
                    setProcessingTime(totalTimeToAudio);
                  }
                }).catch(e => console.error("Playback promise error:", e));
              }
            } catch (e) {
              console.error("Playback error:", e);
            }

            audioElement.onended = () => {
              URL.revokeObjectURL(audioUrl);
            };
          }
        }
      }

      await processChunksSequentially();
    } catch (error) {
      console.error("Error sending audio:", error);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen p-4">
      <Card className="w-96 p-4 shadow-lg">
        <CardContent className="flex flex-col items-center gap-4">
          <h2 className="text-xl font-bold">AI Voice Recorder</h2>
          <div className="flex flex-col items-center gap-4">
            <div className="relative flex items-center justify-center w-20 h-20">
              {isRecording && (
                <div className="absolute w-full h-full bg-red-500 rounded-full animate-ping opacity-50"></div>
              )}
              {isRecording ? (
                <Button 
                  onClick={stopRecording} 
                  className="bg-red-500 hover:bg-red-600 text-white z-10"
                >
                  <StopCircle className="w-6 h-6" />
                </Button>
              ) : (
                <Button 
                  onClick={startRecording} 
                  className="bg-green-500 hover:bg-green-600 text-white"
                >
                  <Mic className="w-6 h-6" />
                </Button>
              )}
            </div>
            {isRecording && (
              <p className="text-red-500 font-medium">Recording... Click to stop</p>
            )}
            {processingTime !== null && (
              <div className="text-center mt-4">
                <p className="font-medium">Processing Time:</p>
                <p className="text-lg">{processingTime.toFixed(2)} ms</p>
                <p className="text-sm text-gray-500">({(processingTime / 1000).toFixed(2)} seconds)</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}