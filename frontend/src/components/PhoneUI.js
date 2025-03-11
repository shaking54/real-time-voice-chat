import React, { useState } from "react";
import VoiceInput from "./VoiceInput";
import AudioPlayer from "./AudioPlayer";

const PhoneUI = () => {
  const [callActive, setCallActive] = useState(false);
  const [audioUrl, setAudioUrl] = useState(null);

  const startCall = () => {
    setCallActive(true);
  };

  const endCall = () => {
    setCallActive(false);
    setAudioUrl(null);
  };

  const handleAudioResponse = (audioBlob) => {
    const url = URL.createObjectURL(audioBlob);
    setAudioUrl(url);
  };

  return (
    <div className="phone-container">
      {!callActive ? (
        <button className="call-button" onClick={startCall}>
          📞 Call AI
        </button>
      ) : (
        <div className="call-screen">
          <p>📞 Talking to AI...</p>
          <VoiceInput onAudioSend={handleAudioResponse} />
          <button className="end-call-button" onClick={endCall}>
            🔴 End Call
          </button>
          <AudioPlayer audioUrl={audioUrl} />
        </div>
      )}
    </div>
  );
};

export default PhoneUI;