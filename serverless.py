from utils.startup import *
import runpod
import random
import time
import re
import numpy as np
import os
from studio import process, job_queue, settings
from utils.image import image_fetch, image_numpy_to_base64
#from utils.logging import logger
from utils.args import load_precision
from utils.uploader import uploader
from utils.crypto import decrypt, encrypt
from utils.logging import logger
from typing import Optional, Dict
from modules.video_queue import JobStatus, Job
from pydantic import BaseModel, Field
from runpod.serverless.utils.rp_cleanup import clean

class JobInput(BaseModel):
    # Original, F1
    model_type: str = "Original"
    # Positive prompt
    # Example: "[1s: The person waves hello] [3s: The person jumps up and down] [5s: The person does a dance]"
    prompt_text: str
    # Negative prompt
    n_prompt: str = ""
    seed: int = Field(default_factory=lambda: random.randint(0, 4294967295))
    total_second_length: int = 5
    latent_window_size: int = 9
    steps: int = 25
    cfg: float = 1.0
    gs: float = 10.0
    rs: int = 0
    use_teacache: bool = True
    teacache_num_steps: int = 25
    teacache_rel_l1_thresh: float = 0.15
    # Number of sections to blend between prompts
    blend_sections: int = 4
    # Used as a starting point if no image is provided
    latent_type: str = "Black"
    # Select one or more LoRAs to use for this job
    selected_loras: list[str] = Field(default_factory=list)
    resolutionW: int = 640
    resolutionH: int = 640
    
    image_url: str
    
def upload_result(filepath: Optional[str], storage_path: str):
    file_url = uploader.upload_file(filepath, target_path=storage_path)
    file_url = encrypt(file_url).decode()
    return file_url

def cleanup_outputs():
    outputs_path = settings.get("output_dir")
    
    if not os.path.exists(outputs_path):
        os.makedirs(outputs_path)
        return
    
    clean([outputs_path])
    os.makedirs(outputs_path)
    
    

def get_job_progress(data: Dict):
    html = data.get('html', '')
    
    if not html:
        return (None, None)
    
    progress_match = re.search(r'<progress value="(\d+)" max="100"></progress>', html)
    message_match = re.search(r'<span>(.*?)</span>', html)
    
    if progress_match:
        percentage = int(progress_match.group(1))
    else:
        percentage = None
        
    if message_match:
        message = str(message_match.group(1))
    else:
        message = None
        
    return (percentage, message)
                    
async def handler(job):
    """
    Handles a new job by processing it and uploading the result.
    """
    # Validate the job input.
    job_input = JobInput.model_validate(job["input"])
    
    job_image = image_fetch(decrypt(job_input.image_url).decode())
    
    job_args = {
        **job_input.model_dump(),
        "input_image": np.array(job_image),
        "end_frame_image": None,
        "end_frame_strength": None,
        "clean_up_videos": True,
        "lora_loaded_names": [],
    }
    del job_args["image_url"]
    
    response = process(**job_args)
    job_id = response[1]
    
    if not job_id:
        raise Exception("Job ID is none.")
    
    # Location where the outputs will be stored.
    storage_path = f"framepack/{job['id']}"
    
    last_job_status = None  # Track the previous job status to detect status changes
    last_progress_percentage = 0 
    
    PROGRESS_UPDATE_RATE = 5
    
    while True:
        job: Job = job_queue.get_job(job_id)
        
        if not job:
            raise Exception(f"Job not found: {job_id}")
        
        if last_job_status != job.status:
            yield {
                "name": "update",
                "payload": {
                    "status": job.status,
                    "error": job.error,
                    "result": upload_result(job.result, storage_path) if job.status == JobStatus.COMPLETED else None,
                }
            }

        # Handle job status and progress
        if job.status == JobStatus.PENDING:
            position = job_queue.get_queue_position(job_id)
            logger.debug(f"Job {job_id} is pending, position in queue: {position}")

        elif job.status == JobStatus.RUNNING:
            if job.progress_data and 'preview' in job.progress_data:
                (percentage, message) = get_job_progress(job.progress_data)
                
                if last_progress_percentage != percentage:
                    if (percentage < 100 and (last_progress_percentage + PROGRESS_UPDATE_RATE) > percentage):
                        return
            
                    last_progress_percentage = percentage
                    
                    preview = job.progress_data.get('preview')
                    preview_b64 = None if preview is None else image_numpy_to_base64(preview)
                    
                    yield {
                        "name": "progress",
                        "payload": {
                            "percentage": percentage,
                            "preview": preview_b64,
                            "description": job.progress_data.get('desc', ''),
                            "message": message,
                        },
                    }
                    

        elif job.status == JobStatus.COMPLETED:
            # Show the final video and reset the button text
            break

        elif job.status == JobStatus.FAILED:
            # Show error and reset the button text
            break

        elif job.status == JobStatus.CANCELLED:
            # Show cancelled message and reset the button text
            break

        # Update last_job_status for the next iteration
        last_job_status = job.status
        
        # Wait a bit before checking again
        time.sleep(0.5)
        
    # Remove the outputs.        
    cleanup_outputs()


if __name__ == '__main__':
    # Sets torch precision.
    load_precision()
    
    # Start!
    runpod.serverless.start({
        "handler": handler,
        "return_aggregate_stream": True,
    })