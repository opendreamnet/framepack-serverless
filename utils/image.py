import numpy as np
from PIL import Image
import requests
from io import BytesIO
import base64
import os

def image_to_numpy(input_data):
    """
    Converts an image input (File, URL or base64) to a numpy array.
    """
    try:
        if os.path.isfile(input_data):
            with open(input_data, 'rb') as file:
                image = Image.open(file)
        else:
            # URL
            if input_data.startswith(('http://', 'https://')):
                response = requests.get(input_data)
                image = Image.open(BytesIO(response.content))
            else:
                try:
                    image_data = base64.b64decode(input_data)
                    image = Image.open(BytesIO(image_data))
                except base64.binascii.Error:
                    raise ValueError("The input is not a file, valid URL or base64 string.")
        
        return np.array(image)
    except Exception as e:
        raise ValueError(f"Error processing input: {e}")