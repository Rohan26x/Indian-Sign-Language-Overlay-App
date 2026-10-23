import asyncio
import json
import websockets
from typing import Set
from config import WS_HOST, WS_PORT
from database import DatabaseManager
from isl_translator import ISLTranslator
from visual_sequencer import VisualCardSequencer
from audio_capture import AudioCaptureEngine
from asr_processor import ASRProcessor

class PipelineOrchestrator:
    """Coordinates audio capture, ASR transcription, ISL grammar translation, and WebSocket IPC."""

    def __init__(self):
        self.db = DatabaseManager()
        self.translator = ISLTranslator()
        self.sequencer = VisualCardSequencer(self.db)
        self.asr = ASRProcessor()
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.loop: asyncio.AbstractEventLoop = None

        # Audio capture engine with thread-safe async queue dispatch
        self.audio_engine = AudioCaptureEngine(callback=self._on_audio_chunk)

    def _on_audio_chunk(self, chunk):
        """Called when a speech audio buffer is received from the audio capture engine."""
        if self.loop and self.clients:
            text = self.asr.transcribe_chunk(chunk)
            if text:
                asyncio.run_coroutine_threadsafe(self.process_and_broadcast(text, source="audio"), self.loop)

    async def register(self, websocket: websockets.WebSocketServerProtocol):
        self.clients.add(websocket)
        print(f"Client connected from {websocket.remote_address}. Active clients: {len(self.clients)}")
        # Send initial greeting payload
        welcome_payload = {
            "type": "system_status",
            "status": "connected",
            "message": "Connected to ISL Real-Time Translation Pipeline",
            "vocabulary_count": len(self.db.get_all_glosses())
        }
        await websocket.send(json.dumps(welcome_payload))

    async def unregister(self, websocket: websockets.WebSocketServerProtocol):
        self.clients.discard(websocket)
        print(f"Client disconnected. Active clients: {len(self.clients)}")

    async def broadcast(self, message: dict):
        if self.clients:
            data = json.dumps(message)
            coros = [client.send(data) for client in list(self.clients)]
            if coros:
                await asyncio.gather(*coros, return_exceptions=True)

    async def process_and_broadcast(self, text: str, source: str = "text"):
        """Runs the translation and visual sequencer pipeline and broadcasts to overlay frontend."""
        if not text or not text.strip():
            return

        # Step 1: ISL Syntactic Translation (SVO -> SOV + NMM extraction)
        translation_result = self.translator.translate(text)

        # Step 2: Visual & Skeletal Sequence Resolution
        animation_sequence = self.sequencer.sequence_glosses(translation_result["isl_glosses"])

        payload = {
            "type": "isl_translation",
            "source": source,
            "original_text": translation_result["original_text"],
            "isl_glosses": translation_result["isl_glosses"],
            "nmm": translation_result["nmm"],
            "is_question": translation_result["is_question"],
            "sequence": animation_sequence
        }

        print(f"[{source.upper()}] '{text}' -> ISL: {translation_result['isl_glosses']} (NMM: {translation_result['nmm']})")
        await self.broadcast(payload)

    async def handle_message(self, websocket: websockets.WebSocketServerProtocol, message_str: str):
        try:
            msg = json.loads(message_str)
            msg_type = msg.get("type")

            if msg_type == "translate_text":
                text = msg.get("text", "")
                await self.process_and_broadcast(text, source="user_input")

            elif msg_type == "start_audio":
                self.audio_engine.start()
                await self.broadcast({"type": "audio_status", "status": "recording"})

            elif msg_type == "stop_audio":
                self.audio_engine.stop()
                await self.broadcast({"type": "audio_status", "status": "stopped"})

            elif msg_type == "ping":
                await websocket.send(json.dumps({"type": "pong"}))

        except Exception as e:
            print(f"Error handling message: {e}")
            await websocket.send(json.dumps({"type": "error", "error": str(e)}))

    async def run_server(self):
        self.loop = asyncio.get_running_loop()
        print(f"Starting ISL WebSocket Server on ws://{WS_HOST}:{WS_PORT} ...")

        async def handler(websocket):
            await self.register(websocket)
            try:
                async for message in websocket:
                    await self.handle_message(websocket, message)
            except websockets.exceptions.ConnectionClosed:
                pass
            finally:
                await self.unregister(websocket)

        async with websockets.serve(handler, WS_HOST, WS_PORT):
            print(f"ISL Translation Server is live and listening on ws://{WS_HOST}:{WS_PORT}")
            await asyncio.Future() # Run forever

def main():
    orchestrator = PipelineOrchestrator()
    try:
        asyncio.run(orchestrator.run_server())
    except KeyboardInterrupt:
        orchestrator.audio_engine.stop()
        print("\nPipeline orchestrator terminated by user.")

if __name__ == "__main__":
    main()
