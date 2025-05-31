import os
import httpx
import re
from studio import settings
from utils.logging import logger
from local_types.runpod_job import JobInputModel

class LoraManager():
    logger = logger.getChild("lora_manager")
    
    def __init__(self):
        self.remote_api_tokens = [
            {
                "url_regex": "huggingface.co",
                "token": os.environ.get("HF_TOKEN", ""),
            },
            {
                "url_regex": "civitai.com",
                "token": os.environ.get("CIVITAI_API_TOKEN", ""),
            }
        ]
  
    def get_http_client(self, url: str):
        headers = {}
        
        for token_data in self.remote_api_tokens:
            if re.search(token_data["url_regex"], url):
                token = token_data["token"]
                
                if token:
                    headers["Authorization"] = f"Bearer {token}"
                    break
        
        return httpx.Client(headers=headers)
    
    # def get_file_name_from_url(self, url: str) -> str:
    #     file_extensions = r'\.(safetensors|pt|bin|ckpt)'
        
    #     file_name_match = re.search(r'/([^/]+{})'.format(file_extensions), url)
    #     if file_name_match:
    #         return file_name_match.group(1)
        
    #     client = self.get_http_client(url)
    #     response = client.head(url, follow_redirects=True)
        
    #     content_disposition = response.headers.get('Content-Disposition', '')
        
    #     if content_disposition:
    #         file_name_match = re.search(r'filename="([^"]+{})"'.format(file_extensions), content_disposition)
    #         if file_name_match:
    #             return file_name_match.group(1)
            
    #     file_name_match = re.search(r'/([^/]+{})'.format(file_extensions), str(response.url))
    #     if file_name_match:
    #         return file_name_match.group(1)
        
    #     raise Exception("Could not determine the filename from the URL.")
    
    def install_model(self, source_url: str, file_path: str):
        client = self.get_http_client(source_url)
        
        self.logger.info(f"Installing model from: {source_url}")
        with client.stream("GET", source_url, follow_redirects=True) as response:
            response.raise_for_status()
            
            with open(file_path, "wb") as file:
                for chunk in response.iter_bytes():
                    file.write(chunk)
                    
            self.logger.info(f"Model installed: {file_path}")
  
    def install_model_if_needed(self, model: JobInputModel):
        lora_dir = settings.get("lora_dir")
        file_path = os.path.join(lora_dir, model.name)
        
        if os.path.exists(file_path):
            self.logger.debug(f"Model already exists: {file_path}")
            return
        
        self.install_model(model.source, file_path)
        
lora_manager = LoraManager()