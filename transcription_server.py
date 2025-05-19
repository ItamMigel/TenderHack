from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import numpy as np
from transformers import pipeline
from download_and_initialize_model import load_model, global_model
import json
from datetime import datetime
import time
import queue
import threading

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the model
if global_model is None:
    global_model = load_model()

model = global_model["model"]
processor = global_model["processor"]
device = global_model["device"]
torch_dtype = global_model["torch_dtype"]

pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    torch_dtype=torch_dtype,
    device=device,
)

# Constants
SAMPLE_RATE = 16000
BLOCK_SIZE = int(SAMPLE_RATE * 20)  # 20 seconds of audio
active_transcriptions = []

def format_time(seconds):
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{int(minutes):02d}:{int(seconds):02d}"

class AudioProcessor:
    def __init__(self):
        self.buffer = np.empty((0, 1), dtype=np.float32)
        self.total_time = 0
        self.audio_queue = queue.Queue()
        
    def process_chunk(self, data):
        try:
            self.buffer = np.concatenate((self.buffer, data))
            
            if len(self.buffer) >= BLOCK_SIZE:
                start_time = self.total_time
                end_time = self.total_time + 20  # 20 seconds block
                self.total_time = end_time

                audio_chunk = self.buffer[:BLOCK_SIZE]
                self.buffer = self.buffer[BLOCK_SIZE:]
                audio_input = audio_chunk.flatten()

                result = pipe(
                    audio_input,
                    generate_kwargs={"language": "ru", "task": "transcribe"}
                )['text'].strip()

                if result not in ['Продолжение следует...', 'Спасибо.']:
                    time_marker = f"{format_time(start_time)}-{format_time(end_time)}"
                    return {
                        'time': time_marker,
                        'text': result,
                        'timestamp': datetime.now().isoformat()
                    }
        except Exception as e:
            print(f"Error processing audio: {e}")
            return None

async def process_transcriptions():
    while True:
        # Keep only last 30 minutes of transcriptions
        current_time = time.time()
        active_transcriptions[:] = [
            t for t in active_transcriptions 
            if (current_time - time.mktime(datetime.fromisoformat(t['timestamp']).timetuple())) < 1800
        ]
        await asyncio.sleep(60)  # Check every minute

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(process_transcriptions())

@app.websocket("/ws/transcribe")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    processor = AudioProcessor()
    
    try:
        while True:
            data = await websocket.receive_bytes()
            audio_data = np.frombuffer(data, dtype=np.float32).reshape(-1, 1)
            
            result = processor.process_chunk(audio_data)
            if result:
                active_transcriptions.append(result)
                await websocket.send_json(result)
                
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

@app.get("/api/summaries")
async def get_summaries():
    # Get all transcriptions from the last 30 minutes
    transcripts = [t['text'] for t in active_transcriptions]
    
    if not transcripts:
        return {"summaries": []}
    
    # For now, just return the transcripts as summaries
    # Later we can integrate with the summarization model
    return {
        "summaries": transcripts
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("transcription_server:app", host="0.0.0.0", port=8000, reload=True)