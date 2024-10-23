import base64 
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import unpad, pad
from Cryptodome.Random import get_random_bytes


key = "G2S0S2HIRE4LINES"
iv =  '12HL56789G2S0S21'.encode('utf-8')


def encrypt_code(data):
    try:
        data= pad(str(data).encode(),16)
        cipher = AES.new(key.encode('utf-8'),AES.MODE_CBC,iv)
        return (base64.b64encode(cipher.encrypt(data)).decode("utf-8", "ignore")).replace("/","_").replace("+","[")
    except Exception as err:
        print("Error in encrypt: ",str(err))
        raise


def decrypt_code(data):
    try:
        enc = base64.b64decode(data.replace("_","/").replace("[","+"))
        cipher = AES.new(key.encode('utf-8'), AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(enc),16).decode("utf-8", "ignore")
    except Exception as err:
        print("Error in decrypt: ",str(err))
        raise


import shortuuid
import jsons
import base64
import requests
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# HELPER FUNCTION
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def calculate_sha256_string(input_string):
    # Create a hash object using the SHA-256 algorithm
    sha256 = hashes.Hash(hashes.SHA256(), backend=default_backend())
    # Update hash with the encoded string
    sha256.update(input_string.encode('utf-8'))
    # Return the hexadecimal representation of the hash
    return sha256.finalize().hex()


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def base64_encode(input_dict):
    # Convert the dictionary to a JSON string
    json_data = jsons.dumps(input_dict)
    # Encode the JSON string to bytes
    data_bytes = json_data.encode('utf-8')
    # Perform Base64 encoding and return the result as a string
    return base64.b64encode(data_bytes).decode('utf-8')

