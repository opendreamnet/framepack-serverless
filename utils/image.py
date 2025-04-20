import numpy as np
import requests
import base64
import os
from PIL import Image
from io import BytesIO
from utils.crypto import decrypt

def image_to_numpy(input_data: str, encrypted = False):
    """
    Converts an image input (File, URL or base64) to a numpy array.
    """
    try:
        if os.path.isfile(input_data):
            with open(input_data, 'rb') as file:
                output = file.read()
        else:
            # URL
            if input_data.startswith(('http://', 'https://')):
                response = requests.get(input_data)
                output = response.content
            else:
                try:
                    output = base64.b64decode(input_data)
                except base64.binascii.Error:
                    raise ValueError("The input is not a file, valid URL or base64 string.")
        
        if encrypted:
            output = decrypt(output)
            
        image = Image.open(BytesIO(output))
        return np.array(image)
    except Exception as e:
        raise ValueError(f"Error processing input: {e}")