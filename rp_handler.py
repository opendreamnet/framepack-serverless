import runpod
import os
import random
from demo_gradio import worker, stream, outputs_folder
from diffusers_helper.thread_utils import async_run
from utils.image import image_to_numpy
from utils.args import _set_target_precision
from utils.rp_upload import upload_video, upload_test_file
from runpod.serverless.utils.rp_cleanup import clean

def handler(job):
    """
    Handles a new job by processing it and uploading the result.
    """
    print(f"New job: {job}")
    
    # Upload a test file to verify that the S3 connection works.
    upload_test_file()
    
    # Set default job input values.
    default_job_input = {
        "n_prompt": "",
        "seed": random.randint(0, 4294967295),
        "total_second_length": 5,
        "latent_window_size": 9,
        "steps": 25,
        "cfg": 1.0,
        "gs": 10.0,
        "rs": 0,
        "gpu_memory_preservation": 6,
        "use_teacache": False,
        "encrypted": False,
    }
    
    # Merge default values with the job's input values.
    job_input = {**default_job_input, **job["input"]}
    
    # Sets if the input and output should be encrypted and 
    # removes the key as is not part of the original function.
    encrypted = job_input["encrypted"]
    del job_input["encrypted"]
    
    # Transforms the input image to a numpy array.
    job_input["input_image"] = image_to_numpy(job_input["input_image"], encrypted)

    # Runs the worker function.
    last_data = None
    output_url = None
    async_run(worker, **job_input)

    while True:
        flag, data = stream.output_queue.next()
        
        if flag == 'file':
            # Saves the last output video data.
            # RunPod charges per second so we focus only on uploading the final file.
            last_data = data
            
        if flag == 'end':
            # Uploads the final output video data.
            if last_data != None:
                output_url = upload_video(job["id"], last_data, encrypted)     
                last_data = None          
                
            break
    
    # Cleans up the `outputs`` folder and creates it again.
    clean(folder_list=[outputs_folder])
    os.makedirs(outputs_folder, exist_ok=True)
    
    return output_url

if __name__ == '__main__':
    # Sets torch precision.
    _set_target_precision()
    
    # Start!
    runpod.serverless.start({
        "handler": handler
    })