import React, { useState, useEffect } from 'react';

const VoiceInput = ({ onSend }) => {
  const [isListening, setIsListening] = useState(false);
  const [recognition, setRecognition] = useState(null);

  useEffect(() => {
    if ('webkitSpeechRecognition' in window) {
      const speechRecognition = new window.webkitSpeechRecognition();
      speechRecognition.continuous = false;
      speechRecognition.interimResults = false;
      speechRecognition.lang = 'en-US';

      speechRecognition.onstart = () => setIsListening(true);
      speechRecognition.onend = () => setIsListening(false);
      speechRecognition.onerror = (event) => {
        console.error('Speech recognition error', event);
        setIsListening(false);
      };
      speechRecognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript.trim();
        onSend(transcript);
      };

      setRecognition(speechRecognition);
    } else {
      console.warn('Speech recognition not supported in this browser.');
    }
  }, [onSend]);

  const handleButtonClick = () => {
    if (recognition) {
      if (isListening) {
        recognition.stop();
      } else {
        recognition.start();
      }
    }
  };

  return (
    <div className="input-container">
      <input type="text" placeholder="Press the microphone to speak" disabled />
      <button onClick={handleButtonClick} disabled={!recognition}>
        {isListening ? 'Stop' : 'Speak'}
      </button>
    </div>
  );
};

export default VoiceInput;
