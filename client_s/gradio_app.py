import gradio as gr
import requests
import io
import numpy as np
import soundfile as sf
import tempfile
import os

# Function to stop recording, call STT API, and trigger LLM & TTS APIs
def stop_recording():
    try:
        # Step 1: Call the STT API
        stt_response = requests.post("http://127.0.0.1:8001/toggle")
        if stt_response.status_code != 200:
            return "Error: STT API failed.", None

        stt_data = stt_response.json()
        transcription = stt_data.get("transcription", "No transcription")
        encrypted_text = stt_data.get("encrypted_text")
        encrypted_key_iv = stt_data.get("encrypted_key_iv")

        # Step 2: Call the LLM API
        llm_response = requests.post(
            "http://127.0.0.1:8002/process",
            json={"encrypted_text": encrypted_text, "encrypted_key_iv": encrypted_key_iv}
        )
        if llm_response.status_code != 200:
            return "Error: LLM API failed.", None

        llm_data = llm_response.json()
        llm_output = llm_data.get("decrypted_text", "No LLM response")
        encrypted_response = llm_data.get("encrypted_response")
        response_key_iv = llm_data.get("response_key_iv")

        # Step 3: Call the TTS API
        tts_response = requests.post(
            "http://127.0.0.1:8003/tts",
            json={"encrypted_response": encrypted_response, "encrypted_key_iv": response_key_iv}
        )
        if tts_response.status_code != 200:
            return llm_output, None

        tts_data = tts_response.json()
        decrypted_text = tts_data.get("decrypted_text", "No text response")
        audio_content_hex = tts_data.get("audio_content")

        # Decode the audio content from hex
        try:
            binary_audio_data = bytes.fromhex(audio_content_hex)
        except Exception as e:
            print(f"Error decoding audio content: {e}")
            return "Error: Invalid audio content.", None

        # Save binary data as a .wav file
        temp_audio_path = os.path.join(tempfile.gettempdir(), "output_audio.wav")
        with open(temp_audio_path, "wb") as f:
            f.write(binary_audio_data)

        # Debugging: Log the outputs
        print(f"Text output: {decrypted_text}")
        print(f"Saved audio file path: {temp_audio_path}")

        return decrypted_text, temp_audio_path

    except Exception as e:
        print(f"Error in stop_recording: {e}")
        return "An unexpected error occurred. Please try again.", None


# Gradio interface
with gr.Blocks() as app:
    gr.Markdown("# Voice Assistant")

    # Trigger Button
    trigger_btn = gr.Button("Trigger Workflow")

    # Outputs: Text and Audio
    output_text = gr.Textbox(label="LLM Response", lines=5)
    audio_output = gr.Audio(label="Play LLM Response", type="filepath")

    # Button Actions
    trigger_btn.click(fn=stop_recording, outputs=[output_text, audio_output])

app.launch()
