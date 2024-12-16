import openai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.backends import default_backend
from langdetect import detect, DetectorFactory
import binascii
import logging
import os

# Initialize logging
logging.basicConfig(level=logging.DEBUG)

# Initialize OpenAI API
openai.api_key = "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"

# Set language detection consistency
DetectorFactory.seed = 0

# Initialize global variables for chat history and language tracking
chat_history = []
last_language = None

# Load RSA private key
try:
    with open(r"C:\Users\SwastikAgarwal\OneDrive - SymphonyAI\vscodefolder\internship@SAI\final_project\projectroot\keys_s\private_key.pem", "rb") as key_file:
        private_key = serialization.load_pem_private_key(key_file.read(), password=None)
except Exception as e:
    logging.error(f"Failed to load private key: {e}")
    raise RuntimeError("Private key could not be loaded. Ensure the file exists and is accessible.")

# Load RSA public key
try:
    with open(r"C:\Users\SwastikAgarwal\OneDrive - SymphonyAI\vscodefolder\internship@SAI\final_project\projectroot\keys_s\public_key.pem", "rb") as key_file:
        public_key = serialization.load_pem_public_key(key_file.read())
except Exception as e:
    logging.error(f"Failed to load public key: {e}")
    raise RuntimeError("Public key could not be loaded. Ensure the file exists and is accessible.")

# Encryption and Decryption Helper Functions
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
    """Decrypt transcription text using AES."""
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

def encrypt_text(text: str, aes_key: bytes, aes_iv: bytes):
    """Encrypt text using AES."""
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(aes_iv), backend=default_backend())
    encryptor = cipher.encryptor()
    padder = sym_padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(text.encode("utf-8")) + padder.finalize()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return encrypted_data.hex()

def encrypt_aes_key_iv(aes_key: bytes, aes_iv: bytes):
    """Encrypt AES key and IV using RSA public key."""
    combined_key_iv = aes_key + aes_iv
    encrypted_key_iv = public_key.encrypt(
        combined_key_iv,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return encrypted_key_iv.hex()

def get_chatbot_response(user_input: str):
    """Generate a chatbot response using OpenAI GPT."""
    global chat_history, last_language

    try:
        # Detect the language of the input
        user_language = detect(user_input)
        logging.debug(f"Detected language: {user_language}")

        # Track language changes
        if last_language is None or last_language != user_language:
            last_language = user_language
            chat_history.append({"role": "system", "content": f"Language switched to {user_language}."})

        # Add user input to chat history
        chat_history.append({"role": "user", "content": user_input})

        # Call OpenAI API for chat completion
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=chat_history
        )
        response_dict = response.model_dump()
        chatbot_response = response_dict['choices'][0]['message']['content'].strip()

        # Append the chatbot response to the chat history
        chat_history.append({"role": "assistant", "content": chatbot_response})
        return chatbot_response
    except Exception as e:
        logging.error(f"Error communicating with OpenAI GPT: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate response from GPT.")

# FastAPI Initialization
app = FastAPI()

# Request and Response Models
class DecryptRequest(BaseModel):
    encrypted_text: str  # Encrypted transcription text as a hex string
    encrypted_key_iv: str  # Encrypted AES key and IV as a hex string

class DecryptResponse(BaseModel):
    # transcription: str  # Decrypted transcription text
    # llm_response: str   # Response from OpenAI GPT
    encrypted_response: str  # Encrypted GPT response
    response_key_iv: str  # Encrypted AES key and IV for response

# API Endpoint
@app.post("/process", response_model=DecryptResponse)
def process_encrypted_text(request: DecryptRequest):
    """Process encrypted transcription text and provide a GPT response."""
    try:
        logging.debug(f"Received encrypted_text: {request.encrypted_text[:50]}...")
        logging.debug(f"Received encrypted_key_iv: {request.encrypted_key_iv}")
        logging.debug(f"Full Request Data: {request.model_dump_json()}")

        # Validate Input
        if not request.encrypted_text or not request.encrypted_key_iv:
            raise HTTPException(status_code=400, detail="Both encrypted_text and encrypted_key_iv are required.")

        # Decrypt AES key and IV
        aes_key, aes_iv = decrypt_aes_key_iv(request.encrypted_key_iv)

        # Decrypt the transcription text
        decrypted_text = decrypt_text(request.encrypted_text, aes_key, aes_iv)
        logging.debug(f"Decrypted transcription text: {decrypted_text}")

        # Get GPT response
        llm_response = get_chatbot_response(decrypted_text)
        logging.debug(f"LLM response: {llm_response}")

        # Encrypt GPT response
        response_aes_key = os.urandom(32)
        response_aes_iv = os.urandom(16)
        encrypted_response = encrypt_text(llm_response, response_aes_key, response_aes_iv)

        # Encrypt AES key and IV for response
        response_key_iv = encrypt_aes_key_iv(response_aes_key, response_aes_iv)

        return DecryptResponse(
            # transcription=decrypted_text,
            # llm_response=llm_response,
            encrypted_response=encrypted_response,
            response_key_iv=response_key_iv
        )

    except HTTPException as e:
        logging.error(f"HTTP Exception: {e.detail}")
        raise e
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
