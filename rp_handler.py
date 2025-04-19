import runpod
from demo_gradio import worker, stream
from diffusers_helper.thread_utils import async_run
from utils.image import image_to_numpy
from utils.args import _set_target_precision

def handler(job):
    job_input = job["input"]
    print(f"Job Input: {job_input}")
    
    job_input["input_image"] = image_to_numpy(job_input["input_image"])

    output_filename = None
    async_run(worker, **job_input)

    while True:
        flag, data = stream.output_queue.next()

        if flag == 'file':
            output_filename = data
            yield output_filename
            
        if flag == 'end':
            yield output_filename
            break
        
    return output_filename

  
if __name__ == '__main__':
    _set_target_precision()
    
    runpod.serverless.start({
        "handler": handler,
        "return_aggregate_stream": True
    })