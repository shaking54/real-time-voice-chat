import VoiceRecorder from "./components/VoiceRecorder";

export default function Home() {
  return (
    <main className="flex flex-col items-center justify-center min-h-screen p-4">
      <h1 className="text-2xl font-bold mb-4">AI Voice Recorder</h1>
      <VoiceRecorder />
    </main>
  );
}
