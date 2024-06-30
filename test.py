import requests
import os
from dotenv import load_dotenv
import sounddevice as sd
import numpy as np
import threading
import queue
import soundfile as sf
import pygame
from openai import OpenAI

# Load your OpenAI API key from environment variables
load_dotenv()

# Set the sampling rate and chunk size
sampling_rate = 44100
chunk_size = 1024  # Record in chunks of 1024 frames

# Flag to control the recording state
is_recording = True

# Queue to collect audio data
audio_queue = queue.Queue()

def record_audio():
    global is_recording
    try:
        # Prepare to record
        print("Recording... (Press Enter to stop)")
        while is_recording:
            # Record a chunk of audio data
            audio_chunk = sd.rec(frames=chunk_size, samplerate=sampling_rate, channels=1, blocking=True)
            # Put the chunk into the queue
            audio_queue.put(audio_chunk)
    except Exception as e:
        print(f"An error occurred: {e}")

def stop_recording():
    global is_recording
    is_recording = False
    recording_thread.join()  # Wait for the recording thread to finish
    # Concatenate all chunks in the queue
    audio_data = np.concatenate(list(audio_queue.queue))
    return audio_data

# Run the recording in a separate thread
recording_thread = threading.Thread(target=record_audio)
recording_thread.start()

# Wait for the Enter key to stop recording
input("Press Enter to stop recording...\n")
audio_data = stop_recording()

print("Recording stopped.")

# Save the recorded audio to a WAV file
output_file = "recorded_audio.wav"
sf.write(output_file, audio_data, samplerate=sampling_rate)
print(f"Audio saved to {output_file}")

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Transcribe the audio using OpenAI Whisper
with open(output_file, "rb") as audio_file:
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )
    print(f"Transcribed text: {transcription.text}")

data = {
    "text": transcription.text,
}
completion = requests.post("https://bob-hackathon.onrender.com/openai/openai-chat", json=data)

print(f"Response: {completion.json()}")

response = client.audio.speech.create(
    model="tts-1",
    voice="nova",
    input=completion.json()['reply'],
)

response_content = response.content
with open("output.mp3", "wb") as f:
    f.write(response_content)


pygame.mixer.init()
pygame.mixer.music.load("output.mp3")

pygame.mixer.music.play()

while pygame.mixer.music.get_busy():
    pygame.time.Clock().tick(10)

os.remove("output.mp3")