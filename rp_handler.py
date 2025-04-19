import runpod
import os
from demo_gradio import worker, stream
from diffusers_helper.thread_utils import async_run
from utils.image import image_to_numpy
from utils.args import _set_target_precision
from utils.rp_upload import upload_video
from runpod.serverless.utils.rp_cleanup import clean

def handler(job):
    print(f"New job: {job}")
    
    job_input = job["input"]
    job_input["input_image"] = image_to_numpy(job_input["input_image"])

    output_url = None
    async_run(worker, **job_input)

    while True:
        flag, data = stream.output_queue.next()

        if flag == 'file':
            output_url = upload_video(job["id"], data, bucket_name=os.environ.get("BUCKET_NAME", None))
            yield output_url
            
        if flag == 'end':
            yield output_url
            break
        
    clean(folder_list=["outputs"])

if __name__ == '__main__':
    _set_target_precision()
    
    runpod.serverless.start({
        "handler": handler,
        "return_aggregate_stream": True
    })