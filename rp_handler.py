import runpod
import signal
from demo_gradio import worker, stream
from diffusers_helper.thread_utils import async_run
from utils.image import image_to_numpy
from utils.args import _set_target_precision
from utils.rp_upload import upload_video, upload_test_file
from runpod.serverless.utils.rp_cleanup import clean
from utils.crypto import decrypt

is_interrupted = False

def signal_handler(sig, frame):
    print('Process interrupted!')
    
    global is_interrupted
    is_interrupted = True

def handler(job):
    print(f"New job: {job}")
    
    upload_test_file()
    
    default_job_input = {
        "n_prompt": "",
        "seed": 31337,
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
    
    job_input = {**default_job_input, **job["input"]}
    
    encrypted = job_input["encrypted"]
    del job_input["encrypted"]
        
    if encrypted:
        job_input["prompt"] = decrypt(job_input["prompt"]).decode()
    
    job_input["input_image"] = image_to_numpy(job_input["input_image"], encrypted)

    output_url = None
    async_run(worker, **job_input)

    while True:
        flag, data = stream.output_queue.next()
        
        if is_interrupted:
            break

        if flag == 'file':
            output_url = upload_video(job["id"], data, encrypted)
            yield output_url
            
        if flag == 'end':
            yield output_url
            break
        
    clean(folder_list=["outputs"])

if __name__ == '__main__':
    _set_target_precision()
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    runpod.serverless.start({
        "handler": handler,
        "return_aggregate_stream": True
    })