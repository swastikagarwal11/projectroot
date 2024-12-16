from fastapi import FastAPI, HTTPException #restapi, errors
from threading import Thread, Lock #for using resources
from pydantic import BaseModel  #structure response model
import whisper 
import pyaudio
import numpy as np
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.backends import default_backend
import os
import base64
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for security in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load RSA public key
with open(r"C:\Users\SwastikAgarwal\OneDrive - SymphonyAI\vscodefolder\internship@SAI\final_project\projectroot\keys_s\public_key.pem", "rb") as key_file:
    public_key = serialization.load_pem_public_key(key_file.read())


# AES Encryption Helper Functions
def generate_aes_key_iv():
    """Generate AES key and IV."""
    return os.urandom(32), os.urandom(16)  # 32 bytes (256-bit key), 16 bytes IV

def encrypt_aes_key_iv(aes_key, aes_iv):
    """Encrypt AES key and IV using RSA."""
    combined_key_iv = aes_key + aes_iv
    encrypted_key_iv = public_key.encrypt(
        combined_key_iv,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted_key_iv
    # return base64.b64encode(encrypted_key_iv).decode()  # Base64 encode

def encrypt_audio(buffer, aes_key, aes_iv):
    """Encrypt audio data or text using AES."""
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(aes_iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = sym_padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(buffer) + padder.finalize()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return encrypted_data

# Whisper model
model = whisper.load_model("base")  # Replace 'base' with 'tiny' or other models for faster performance.

# Audio configuration
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

# Global variables
transcription_text = ""
stop_transcription = False
is_transcribing = False
lock = Lock()
audio = pyaudio.PyAudio()
stream = None
recorded_audio = b""  # Buffer for storing audio data.

class TranscriptionResponse(BaseModel):
    # transcription: str
    # language_code: str  # Language detected by Whisper
    encrypted_text: str  # Encrypted transcription text as a hex string
    # encrypted_audio: str  # Encrypted audio as a hex string
    encrypted_key_iv: str  # Encrypted AES key and IV as a hex string

@app.post("/toggle", response_model=TranscriptionResponse)
def toggle_transcription():
    global stream, stop_transcription, transcription_text, is_transcribing, recorded_audio

    with lock:
        if not is_transcribing:
            # Start transcription
            stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
            stop_transcription = False
            transcription_text = ""
            recorded_audio = b""
            is_transcribing = True
            capture_thread = Thread(target=capture_audio, daemon=True)
            capture_thread.start()
            return {"message": "Transcription started."}
        else:
            # Stop transcription
            stop_transcription = True
            is_transcribing = False
            stream.stop_stream()
            stream.close()

            # Generate AES key and IV
            aes_key, aes_iv = generate_aes_key_iv()

            # Encrypt raw audio
            encrypted_audio = encrypt_audio(recorded_audio, aes_key, aes_iv)

            # Transcribe audio using Whisper
            audio_data = np.frombuffer(recorded_audio, dtype=np.int16).astype(np.float32) / 32768.0
            result = model.transcribe(audio_data, fp16=False)
            transcription_text = result["text"].strip()
            language_code = result.get("language", "unknown")  # Detected language

            # Encrypt transcription text
            encrypted_text = encrypt_audio(transcription_text.encode('utf-8'), aes_key, aes_iv)

            # Encrypt AES key and IV using RSA
            encrypted_key_iv = encrypt_aes_key_iv(aes_key, aes_iv)

            return {
                # "transcription": transcription_text,
                # "language_code": language_code,
                "encrypted_text": encrypted_text.hex(),
                # "encrypted_audio": encrypted_audio.hex(),
                "encrypted_key_iv": encrypted_key_iv.hex()
            }

def capture_audio():
    global stop_transcription, recorded_audio
    while not stop_transcription:
        data = stream.read(CHUNK, exception_on_overflow=False)
        recorded_audio += data

@app.on_event("shutdown")
def shutdown_event():
    global audio
    audio.terminate()

