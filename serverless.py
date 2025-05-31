from utils.startup import *
import runpod

import time
import re
import numpy as np
import os
from studio import process, job_queue, settings, lora_names
from utils.image import image_fetch, image_numpy_to_base64
from utils.args import load_precision
from utils.uploader import uploader
from utils.crypto import decrypt, encrypt
from utils.logging import logger
from local_types.runpod_job import JobInput
from typing import Optional, Dict
from modules.video_queue import JobStatus, Job
from modules.lora_manager import lora_manager
from runpod.serverless.utils.rp_cleanup import clean
    
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
    logger.info(f"Received job: {job_input}")
    
    job_image = image_fetch(decrypt(job_input.image_url).decode())
    
    selected_loras: list[str] = []
    lora_values: list[str] = []
    
    for lora in job_input.loras:
        lora_manager.install_model_if_needed(lora)
        lora_name, _ = os.path.splitext(lora.name)
        
        if lora_name not in lora_names:
            lora_names.append(lora_name)
            
        selected_loras.append(lora_name)
        lora_values.append(lora.weight)
    
    job_args = {
        **job_input.config.model_dump(),
        "input_image": np.array(job_image),
        "end_frame_image": None,
        "end_frame_strength": None,
        "clean_up_videos": True,
        "lora_loaded_names": lora_names,
        "selected_loras": selected_loras,
        "lora_values": lora_values,
    }
    
    response = process(**job_args)
    job_id = response[1]
    
    if not job_id:
        raise Exception("Job ID is none.")
    
    logger.info(f"Create job id: {job_id}")
    
    # Location where the outputs will be stored.
    storage_path = f"framepack/{job['id']}"
    
    last_job_status = None  # Track the previous job status to detect status changes
    last_progress_percentage = -1
    current_second = 1
    
    PROGRESS_UPDATE_RATE = 5
    
    while True:
        job: Job = job_queue.get_job(job_id)
        
        if not job:
            raise Exception(f"Job not found: {job_id}")
        
        if last_job_status != job.status:
            logger.info(f"-> {job.status}")
            
            yield {
                "name": "update",
                "payload": {
                    "status": job.status.value,
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
                
                # The percentage is now lower than the last saved, this happens because we have advanced to the next second of the video.
                if last_progress_percentage >= 90 and percentage < last_progress_percentage:
                    current_second += 1
                    last_progress_percentage = -1
                
                if last_progress_percentage != percentage:
                    logger.info(f"-> {percentage}% - Second: {current_second} - {message}")
                    
                    if ((last_progress_percentage + PROGRESS_UPDATE_RATE) < percentage):
                        last_progress_percentage = percentage
                        preview_b64 = None
                        
                        prev_percentage = 100 * (current_second - 1)
                        total_percentage = round((prev_percentage + percentage) / (100 * job_input.config.total_second_length)) * 100
                        
                        try:
                            preview = job.progress_data.get('preview')
                            preview_b64 = None if preview is None else image_numpy_to_base64(preview)
                        except Exception as e:
                            logger.warning(f"Error converting preview to base64: {e}")
                        
                        yield {
                            "name": "progress",
                            "payload": {
                                "percentage": total_percentage,
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