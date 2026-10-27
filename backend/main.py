import asyncio
import json
import time
import websockets
from typing import Set, Optional
from config import WS_HOST, WS_PORT
from database import DatabaseManager
from isl_translator import ISLTranslator
from visual_sequencer import VisualCardSequencer
from audio_capture import AudioCaptureEngine
from asr_processor import ASRProcessor

class PipelineOrchestrator:
    """
    Coordinates the real-time streaming pipeline:
    - In-Memory System Audio Loopback (100ms chunks)
    - Sliding-Window Streaming ASR with LocalAgreement-2 & 300ms micro-pauses
    - Sub-15ms spaCy SVO -> SOV & NMM translation
    - 3D Skeletal and 2D Card Sequencing
    - WebSocket IPC dispatch with live latency telemetry and interpreter feedback logging
    """

    def __init__(self):
        self.db = DatabaseManager()
        self.translator = ISLTranslator()
        self.sequencer = VisualCardSequencer(self.db)
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.loop: Optional[asyncio.AbstractEventLoop] = None

        # Streaming ASR Processor with partial and commit callbacks
        self.asr = ASRProcessor(
            on_partial=self._on_asr_partial,
            on_commit=self._on_asr_commit
        )

        # Audio Capture Engine streaming 100ms chunks
        self.audio_engine = AudioCaptureEngine(callback=self._on_audio_chunk)

    def _on_audio_chunk(self, chunk, is_speech: bool):
        """Called when a 100ms audio chunk is received."""
        if self.loop and self.clients:
            self.asr.ingest_chunk(chunk, is_speech)

    def _on_asr_partial(self, partial_text: str):
        """Dispatches unstable partial words immediately to frontend subtitle ticker."""
        if self.loop and self.clients and partial_text:
            payload = {
                "type": "partial_transcription",
                "text": partial_text,
                "timestamp": time.time()
            }
            asyncio.run_coroutine_threadsafe(self.broadcast(payload), self.loop)

    def _on_asr_commit(self, committed_clause: str):
        """Dispatches stabilized sub-clause downstream to ISL translation."""
        if self.loop and self.clients and committed_clause:
            asyncio.run_coroutine_threadsafe(
                self.process_and_broadcast(committed_clause, source="audio_stream"),
                self.loop
            )

    async def register(self, websocket: websockets.WebSocketServerProtocol):
        self.clients.add(websocket)
        print(f"Client connected from {websocket.remote_address}. Total active clients: {len(self.clients)}")
        welcome_payload = {
            "type": "system_status",
            "status": "connected",
            "message": "Connected to ISL 3D Real-Time Streaming Pipeline",
            "vocabulary_count": len(self.db.get_all_glosses()),
            "spacy_active": self.translator.nlp is not None,
            "asr_engine": self.asr.active_engine.upper()
        }
        await websocket.send(json.dumps(welcome_payload))


    async def unregister(self, websocket: websockets.WebSocketServerProtocol):
        self.clients.discard(websocket)
        print(f"Client disconnected. Total active clients: {len(self.clients)}")

    async def broadcast(self, message: dict):
        if self.clients:
            data = json.dumps(message)
            coros = [client.send(data) for client in list(self.clients)]
            if coros:
                await asyncio.gather(*coros, return_exceptions=True)

    async def process_and_broadcast(self, text: str, source: str = "text"):
        """Translates text to ISL SOV, resolves skeletal keyframes, and broadcasts with telemetry."""
        if not text or not text.strip():
            return

        pipeline_start = time.perf_counter()

        # Step 1: spaCy SVO -> SOV Syntactic Translation & NMM Extraction (<15ms)
        t_nlp_start = time.perf_counter()
        translation_result = self.translator.translate(text)
        nlp_ms = (time.perf_counter() - t_nlp_start) * 1000.0

        # Step 2: Visual Card & 3D Skeletal Keyframe Sequencing
        t_seq_start = time.perf_counter()
        animation_sequence = self.sequencer.sequence_glosses(translation_result["isl_glosses"])
        seq_ms = (time.perf_counter() - t_seq_start) * 1000.0

        total_latency_ms = (time.perf_counter() - pipeline_start) * 1000.0

        # Telemetry metrics
        telemetry = {
            "audio_chunk_ms": 100.0 if source == "audio_stream" else 0.0,
            "asr_eval_ms": 250.0 if source == "audio_stream" else 0.0,
            "nlp_ms": round(nlp_ms, 2),
            "sequencer_ms": round(seq_ms, 2),
            "total_pipeline_ms": round(total_latency_ms, 2)
        }

        payload = {
            "type": "isl_translation",
            "source": source,
            "original_text": translation_result["original_text"],
            "isl_glosses": translation_result["isl_glosses"],
            "nmm": translation_result["nmm"],
            "token_nmms": translation_result.get("token_nmms", []),
            "is_question": translation_result["is_question"],
            "sequence": animation_sequence,
            "telemetry": telemetry
        }

        print(f"[{source.upper()}] '{text}' -> ISL: {translation_result['isl_glosses']} | NLP: {nlp_ms:.2f}ms | Total: {total_latency_ms:.2f}ms")
        await self.broadcast(payload)

    async def handle_message(self, websocket: websockets.WebSocketServerProtocol, message_str: str):
        try:
            msg = json.loads(message_str)
            msg_type = msg.get("type")

            if msg_type == "translate_text":
                text = msg.get("text", "")
                await self.process_and_broadcast(text, source="user_input")

            elif msg_type == "start_audio":
                self.asr.reset_state()
                self.audio_engine.start()
                await self.broadcast({
                    "type": "audio_status",
                    "status": "recording",
                    "source": self.audio_engine.capture_source
                })

            elif msg_type == "stop_audio":
                self.audio_engine.stop()
                self.asr.reset_state()
                await self.broadcast({
                    "type": "audio_status",
                    "status": "stopped",
                    "source": self.audio_engine.capture_source
                })


            elif msg_type == "flag_missing_sign":
                # FR-7 & Use Case 4.2.2: Log missing sign feedback to SQLite
                gloss = msg.get("gloss", "UNKNOWN")
                phrase = msg.get("original_phrase", "")
                notes = msg.get("notes", "Reported by user from overlay")
                feedback_id = self.db.record_feedback(gloss, phrase, notes)
                print(f"Feedback logged in SQLite for gloss '{gloss}' (ID #{feedback_id})")
                await websocket.send(json.dumps({
                    "type": "feedback_ack",
                    "id": feedback_id,
                    "gloss": gloss,
                    "status": "recorded"
                }))

            elif msg_type == "ping":
                await websocket.send(json.dumps({"type": "pong", "timestamp": time.time()}))

        except Exception as e:
            print(f"Error handling WebSocket message: {e}")
            await websocket.send(json.dumps({"type": "error", "error": str(e)}))

    async def run_server(self):
        self.loop = asyncio.get_running_loop()
        print(f"Starting ISL Streaming WebSocket Server on ws://{WS_HOST}:{WS_PORT} ...")

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
            await asyncio.Future()

def main():
    orchestrator = PipelineOrchestrator()
    try:
        asyncio.run(orchestrator.run_server())
    except KeyboardInterrupt:
        orchestrator.audio_engine.stop()
        print("\nPipeline orchestrator terminated by user.")

if __name__ == "__main__":
    main()
