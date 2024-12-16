# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
# from cryptography.hazmat.primitives.asymmetric import padding
# from cryptography.hazmat.primitives import serialization, hashes, padding as sym_padding
# from cryptography.hazmat.backends import default_backend
# import pyttsx3
# import binascii
# import logging

# # Initialize logging
# logging.basicConfig(level=logging.DEBUG)

# # Load RSA private key (same as used in STT and LLM APIs)
# try:
#     with open(r"C:\Users\SwastikAgarwal\OneDrive - SymphonyAI\vscodefolder\internship@SAI\final_project\projectroot\keys_s\private_key.pem", "rb") as key_file:
#         private_key = serialization.load_pem_private_key(key_file.read(), password=None)
# except Exception as e:
#     logging.error(f"Failed to load private key: {e}")
#     raise RuntimeError("Private key could not be loaded. Ensure the file exists and is accessible.")

# # Decryption Helper Functions
# def decrypt_aes_key_iv(encrypted_key_iv: str):
#     """Decrypt AES key and IV using RSA private key."""
#     try:
#         combined_key_iv = private_key.decrypt(
#             bytes.fromhex(encrypted_key_iv),
#             padding.OAEP(
#                 mgf=padding.MGF1(algorithm=hashes.SHA256()),
#                 algorithm=hashes.SHA256(),
#                 label=None
#             )
#         )
#         aes_key = combined_key_iv[:32]
#         aes_iv = combined_key_iv[32:]
#         logging.debug(f"Decrypted AES Key: {aes_key.hex()}")
#         logging.debug(f"Decrypted AES IV: {aes_iv.hex()}")
#         return aes_key, aes_iv
#     except Exception as e:
#         logging.error(f"Error decrypting AES key and IV: {e}")
#         raise HTTPException(status_code=500, detail="Failed to decrypt AES key and IV.")

# def decrypt_text(encrypted_text: str, aes_key: bytes, aes_iv: bytes):
#     """Decrypt text using AES."""
#     try:
#         cipher = Cipher(algorithms.AES(aes_key), modes.CBC(aes_iv), backend=default_backend())
#         decryptor = cipher.decryptor()
#         unpadder = sym_padding.PKCS7(algorithms.AES.block_size).unpadder()
#         decrypted_padded_data = decryptor.update(bytes.fromhex(encrypted_text)) + decryptor.finalize()
#         decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()
#         return decrypted_data.decode("utf-8")
#     except binascii.Error as e:
#         logging.error(f"Invalid hexadecimal input for text: {e}")
#         raise HTTPException(status_code=400, detail="Invalid hexadecimal input for encrypted text.")
#     except ValueError as e:
#         logging.error(f"Decryption failed: {e}")
#         raise HTTPException(status_code=400, detail="Failed to decrypt text. Possibly due to incorrect key or corrupted data.")

# # Initialize FastAPI
# app = FastAPI()

# # Pydantic Models
# class TTSRequest(BaseModel):
#     encrypted_response: str  # Encrypted LLM response
#     encrypted_key_iv: str  # Encrypted AES key and IV

# class TTSResponse(BaseModel):
#     decrypted_text: str
#     # message: str

# @app.post("/tts", response_model=TTSResponse)
# def tts_api(request: TTSRequest):
#     """Process encrypted LLM response and optionally synthesize speech."""
#     try:
#         logging.debug(f"Received encrypted_response: {request.encrypted_response[:50]}...")
#         logging.debug(f"Received encrypted_key_iv: {request.encrypted_key_iv}")

#         # Validate Input
#         if not request.encrypted_response or not request.encrypted_key_iv:
#             raise HTTPException(status_code=400, detail="Both encrypted_response and encrypted_key_iv are required.")

#         # Decrypt AES key and IV
#         aes_key, aes_iv = decrypt_aes_key_iv(request.encrypted_key_iv)

#         # Decrypt the LLM response
#         decrypted_text = decrypt_text(request.encrypted_response, aes_key, aes_iv)
#         logging.debug(f"Decrypted LLM response: {decrypted_text}")

#         # Synthesize speech (optional)
#         synthesize_speech(decrypted_text)

#         return {"decrypted_text": decrypted_text, "message": "completed"}
#     except HTTPException as e:
#         logging.error(f"HTTP Exception: {e.detail}")
#         raise e
#     except Exception as e:
#         logging.error(f"Unexpected error: {e}")
#         raise HTTPException(status_code=500, detail="An unexpected error occurred.")

# def synthesize_speech(text):
#     """Synthesize speech from the given text."""
#     try:
#         engine = pyttsx3.init()
#         engine.setProperty("rate", 150)  # Speech rate
#         engine.say(text)
#         engine.runAndWait()
#     except Exception as e:
#         logging.error(f"Error in speech synthesis: {e}")
#         raise HTTPException(status_code=500, detail="Error in speech synthesis.")



from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes, padding as sym_padding
from cryptography.hazmat.backends import default_backend
import pyttsx3
import tempfile
import os
import binascii
import logging

# Initialize logging
logging.basicConfig(level=logging.DEBUG)

# Load RSA private key (same as used in STT and LLM APIs)
try:
    with open(r"C:\Users\SwastikAgarwal\OneDrive - SymphonyAI\vscodefolder\internship@SAI\final_project\projectroot\keys_s\private_key.pem", "rb") as key_file:
        private_key = serialization.load_pem_private_key(key_file.read(), password=None)
except Exception as e:
    logging.error(f"Failed to load private key: {e}")
    raise RuntimeError("Private key could not be loaded. Ensure the file exists and is accessible.")

# Decryption Helper Functions
def decrypt_aes_key_iv(encrypted_key_iv: str):
    """Decrypt AES key and IV using RSA private key."""
    try:
        combined_key_iv = private_key.decrypt(
            bytes.fromhex(encrypted_key_iv),
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        aes_key = combined_key_iv[:32]
        aes_iv = combined_key_iv[32:]
        logging.debug(f"Decrypted AES Key: {aes_key.hex()}")
        logging.debug(f"Decrypted AES IV: {aes_iv.hex()}")
        return aes_key, aes_iv
    except Exception as e:
        logging.error(f"Error decrypting AES key and IV: {e}")
        raise HTTPException(status_code=500, detail="Failed to decrypt AES key and IV.")

def decrypt_text(encrypted_text: str, aes_key: bytes, aes_iv: bytes):
    """Decrypt text using AES."""
    try:
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(aes_iv), backend=default_backend())
        decryptor = cipher.decryptor()
        unpadder = sym_padding.PKCS7(algorithms.AES.block_size).unpadder()
        decrypted_padded_data = decryptor.update(bytes.fromhex(encrypted_text)) + decryptor.finalize()
        decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()
        return decrypted_data.decode("utf-8")
    except binascii.Error as e:
        logging.error(f"Invalid hexadecimal input for text: {e}")
        raise HTTPException(status_code=400, detail="Invalid hexadecimal input for encrypted text.")
    except ValueError as e:
        logging.error(f"Decryption failed: {e}")
        raise HTTPException(status_code=400, detail="Failed to decrypt text. Possibly due to incorrect key or corrupted data.")

# Initialize FastAPI
app = FastAPI()

# Pydantic Models
class TTSRequest(BaseModel):
    encrypted_response: str  # Encrypted LLM response
    encrypted_key_iv: str  # Encrypted AES key and IV

@app.post("/tts")
def tts_api(request: TTSRequest):
    """Process encrypted LLM response, synthesize speech, and return both text and audio content."""
    try:
        logging.debug(f"Received encrypted_response: {request.encrypted_response[:50]}...")
        logging.debug(f"Received encrypted_key_iv: {request.encrypted_key_iv}")

        # Validate Input
        if not request.encrypted_response or not request.encrypted_key_iv:
            raise HTTPException(status_code=400, detail="Both encrypted_response and encrypted_key_iv are required.")

        # Decrypt AES key and IV
        aes_key, aes_iv = decrypt_aes_key_iv(request.encrypted_key_iv)

        # Decrypt the LLM response
        decrypted_text = decrypt_text(request.encrypted_response, aes_key, aes_iv)
        logging.debug(f"Decrypted LLM response: {decrypted_text}")

        # Synthesize speech and save to a temporary file
        audio_path = synthesize_speech_to_file(decrypted_text)

        # Read the audio file content to return it as bytes
        with open(audio_path, "rb") as audio_file:
            audio_content = audio_file.read()

        # Return both text and audio content
        return JSONResponse(
            content={
                "decrypted_text": decrypted_text,
                "audio_content": audio_content.hex(),  # Send audio as a hex-encoded string
            }
        )
    except HTTPException as e:
        logging.error(f"HTTP Exception: {e.detail}")
        raise e
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")

def synthesize_speech_to_file(text: str):
    """Synthesize speech from text and save it to a temporary file."""
    try:
        engine = pyttsx3.init()
        engine.setProperty("rate", 150)  # Speech rate

        # Create a temporary file to save the synthesized speech
        temp_dir = tempfile.gettempdir()
        audio_path = os.path.join(temp_dir, "synthesized_audio.wav")
        
        # Save speech to the temporary file
        engine.save_to_file(text, audio_path)
        engine.runAndWait()

        logging.debug(f"Audio saved to {audio_path}")
        return audio_path
    except Exception as e:
        logging.error(f"Error in speech synthesis: {e}")
        raise HTTPException(status_code=500, detail="Error in speech synthesis.")
