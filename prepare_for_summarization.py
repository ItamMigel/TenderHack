import sounddevice as sd
import numpy as np
import queue
import threading
import random
import time
from transformers import pipeline
from download_and_initialize_model import load_model, global_model

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

sample_rate = 16000
audio_q = queue.Queue()


def audio_callback(indata, frames, time_info, status):
    if status:
        print("Статус:", status)
    audio_q.put(indata.copy())


def format_time(seconds):
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{int(minutes):02d}-{int(seconds):02d}"


def process_audio():
    buffer = np.empty((0, 1), dtype=np.float32)
    total_time = 0
    block_duration = random.randint(20, 30)
    current_block_size = int(sample_rate * block_duration)

    while True:
        try:
            data = audio_q.get(timeout=1)
            buffer = np.concatenate((buffer, data))
            if len(buffer) >= current_block_size:
                start_time = total_time
                end_time = total_time + block_duration
                total_time = end_time

                audio_chunk = buffer[:current_block_size]
                buffer = buffer[current_block_size:]
                audio_input = audio_chunk.flatten()

                result = pipe(
                    audio_input,
                    generate_kwargs={"language": "ru", "task": "transcribe"}
                )['text'].strip()

                if result not in ['Продолжение следует...', 'Спасибо.']:
                    time_marker = f"{format_time(start_time)}-{format_time(end_time)}"
                    print([time_marker, result])

                block_duration = random.randint(20, 30)
                current_block_size = int(sample_rate * block_duration)

        except queue.Empty:
            continue


processing_thread = threading.Thread(target=process_audio, daemon=True)
processing_thread.start()

with sd.InputStream(callback=audio_callback, channels=1, samplerate=sample_rate):
    print("Начинается стриминг аудио. Нажмите Ctrl+C для остановки.")
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Остановка стриминга.")
