import os
import requests
from dotenv import load_dotenv
import pygame
from openai import OpenAI
import gradio as gr

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def decipher(audio_path=None, text_input=None):
    if audio_path:
        # Transcribe the laudio using OpenAI Whisper
        with open(audio_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        transcribed_text = transcription.text
        print(f"Transcribed text: {transcribed_text}")
        combined_text = transcribed_text
    elif text_input:
        combined_text = text_input
    else:
        return "No input provided", None

    # Post the combined text to the chat API
    data = {"text": combined_text}
    completion_response = requests.post("https://bob-hackathon.onrender.com/openai/openai-chat", json=data)
    completion_reply = completion_response.json().get('reply')
    print(f"Response: {completion_reply}")

    # Create speech using the TTS model
    speech_response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=completion_reply,
    )
    response_content = speech_response.content
    with open("output.mp3", "wb") as f:
        f.write(response_content)

    # Play the generated speech
    pygame.mixer.init()
    pygame.mixer.music.load("output.mp3")
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    os.remove("output.mp3")
    return completion_reply, "output.mp3"

# Create Gradio interface with multiple optional inputs
interface = gr.Interface(
    fn=decipher, 
    inputs=[
        gr.Audio(type="filepath",), 
        gr.Textbox(label="Additional Text")
    ], 
    outputs=["text", gr.Audio(type="filepath",)]
)

interface.launch()
