import base64
import requests
import os
import logging
import numpy as np
from PIL import Image
from io import BytesIO
from tenacity import before_sleep_log, retry, stop_after_attempt, wait_fixed
from .logging import logger

logger = logger.getChild("image")

@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(0.2),
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
def image_fetch(input: str) -> Image.Image:
    """
    Converts an image input (File, URL or base64) to a PIL Image.
    """
    try:
        if input.startswith(('http://', 'https://')):
            logger.info(f"Downloading image: {os.path.basename(input)}")
            response = requests.get(input, stream=True)
            output = response.content
        elif os.path.isfile(input):
            logger.info(f"Opening image from: {input}")
            return Image.open(input)
        else:
            logger.info(f"Decoding base64 image: {input[:10]}...")
            output = base64.b64decode(input)

        return Image.open(BytesIO(output))
    except Exception as e:
        raise ValueError(f"Error fetching image: {e}")

def image_numpy_to_base64(array: np.ndarray) -> str:
    image = Image.fromarray(array)
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    
    b64 = base64.b64encode(buffered.getvalue())
    return "data:image/jpeg;base64," + b64.decode()
    
    
    