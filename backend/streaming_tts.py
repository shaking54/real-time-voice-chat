from RealtimeTTS import TextToAudioStream, CoquiEngine, AzureEngine, ElevenlabsEngine

engine = CoquiEngine() # replace with your TTS engine
stream = TextToAudioStream(engine)
stream.feed("Hello world! How are you today?").play(log_synthesized_text=True)
