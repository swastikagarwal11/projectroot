# Voice Assistant Project

This project is a comprehensive voice assistant pipeline integrating Speech-to-Text (STT), Large Language Model (LLM), and Text-to-Speech (TTS) functionalities. It leverages FastAPI for the backend APIs, Gradio for the interface, and cryptographic techniques for secure data transmission.

---

## **Project Structure**

- **llm_api.py**: Handles encrypted text processing, GPT-based responses, and returns encrypted outputs.
- **stt_api.py**: Converts live audio into encrypted transcriptions using the Whisper model.
- **tts_api.py**: Converts encrypted responses into speech using pyttsx3.
- **gradio_interface.py**: Provides a user-friendly interface for triggering and interacting with the voice assistant.

---

## **Key Features**

1. **Speech-to-Text (STT)**:
   - Uses the Whisper model to transcribe audio in real-time.
   - Encrypts transcriptions with AES and RSA for secure transfer.

2. **Large Language Model (LLM)**:
   - Processes encrypted inputs to generate context-aware responses.
   - Returns encrypted responses for further use.

3. **Text-to-Speech (TTS)**:
   - Converts LLM responses to audio using pyttsx3.
   - Ensures secure decryption and playback.

4. **Secure Communication**:
   - RSA and AES encryption/decryption ensures end-to-end security.

5. **Gradio Interface**:
   - Simplified interface to trigger workflows and review outputs.

---

## **Setup Instructions**

### **1. Clone the Repository**
```bash
git clone <repository-url>
cd <repository-directory>


pip install -r requirements.txt



Place RSA private and public keys in the keys_s folder under the projectroot directory. Ensure the paths in the code match your setup.



# Start STT API
uvicorn stt_api:app --host 127.0.0.1 --port 8001

# Start LLM API
uvicorn llm_api:app --host 127.0.0.1 --port 8002

# Start TTS API
uvicorn tts_api:app --host 127.0.0.1 --port 8003




python gradio_interface.py
