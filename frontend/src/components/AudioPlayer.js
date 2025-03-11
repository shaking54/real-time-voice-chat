import React, { useRef, useEffect } from "react";

const AudioPlayer = ({ audioUrl }) => {
  const audioRef = useRef(null);

  useEffect(() => {
    if (audioUrl && audioRef.current) {
      audioRef.current.src = audioUrl;
      audioRef.current.play();
    }
  }, [audioUrl]);

  return <audio ref={audioRef} style={{ display: "none" }} />;
};

export default AudioPlayer;