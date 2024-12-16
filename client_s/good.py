
# import gradio as gr
# import requests
# import io
# import numpy as np
# import soundfile as sf

# # Function to stop recording, call STT API, and trigger LLM & TTS APIs
# def stop_recording():
#     try:
#         # Step 1: Call the STT API
#         stt_response = requests.post("http://127.0.0.1:8001/toggle")
#         # print(f"STT API Response: {stt_response.status_code}, {stt_response.text}")
#         if stt_response.status_code != 200:
#             return "Error: STT API failed.", None

#         stt_data = stt_response.json()
#         transcription = stt_data.get("transcription", "No transcription")
#         encrypted_text = stt_data.get("encrypted_text")
#         encrypted_key_iv = stt_data.get("encrypted_key_iv")
#         # print(f"STT Transcription: {transcription}")
#         # print(f"Encrypted Text: {encrypted_text}")
#         # print(f"Encrypted Key IV: {encrypted_key_iv}")

#         # Step 2: Call the LLM API
#         llm_response = requests.post(
#             "http://127.0.0.1:8002/process",
#             json={"encrypted_text": encrypted_text, "encrypted_key_iv": encrypted_key_iv}
#         )
#         # print(f"LLM API Response: {llm_response.status_code}, {llm_response.text}")
#         if llm_response.status_code != 200:
#             return "Error: LLM API failed.", None

#         llm_data = llm_response.json()
#         llm_output = llm_data.get("decrypted_text", "No LLM response")
#         encrypted_response = llm_data.get("encrypted_response")
#         response_key_iv = llm_data.get("response_key_iv")
#         # print(f"LLM Output: {llm_output}")
#         # print(f"Encrypted Response: {encrypted_response}")
#         # print(f"Response Key IV: {response_key_iv}")

#         # Step 3: Call the TTS API
#         tts_response = requests.post(
#             "http://127.0.0.1:8003/tts",
#             json={"encrypted_response": encrypted_response, "encrypted_key_iv": response_key_iv},
#             stream=True
#         )
#         print(f"TTS API Response: {tts_response.status_code}, {tts_response.text}")
#         if tts_response.status_code != 200:
#             return llm_output, None

#         # Convert audio stream to NumPy array
#         audio_data = io.BytesIO(tts_response.content)
#         audio, sample_rate = sf.read(audio_data)
#         return llm_output, (audio, sample_rate)
#     except Exception as e:
#         print(f"Error in stop_recording: {e}")
#         return "An unexpected error occurred. Please try again.", None


# # Gradio interface
# with gr.Blocks() as app:
#     gr.Markdown("# Voice Assistant")

#     # Trigger Button
#     trigger_btn = gr.Button("Trigger Workflow")

#     # Outputs: Text and Audio
#     output_text = gr.Textbox(label="LLM Response", lines=5)
#     audio_output = gr.Audio(label="Play LLM Response", type="numpy")

#     # Button Actions
#     trigger_btn.click(fn=stop_recording, outputs=[output_text, audio_output])

# app.launch()


