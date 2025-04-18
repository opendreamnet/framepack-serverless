import argparse
import os
import torch
from diffusers_helper.memory import get_cuda_free_memory_gb

default_precision = os.getenv("FRAMEPACK_PRECISION", "auto").lower()

parser = argparse.ArgumentParser()
parser.add_argument('--share', action='store_true')
parser.add_argument("--server", type=str, default='0.0.0.0')
parser.add_argument("--port", type=int, required=False)
parser.add_argument("--inbrowser", action='store_true')
parser.add_argument("--precision", type=str, choices=['auto', 'fp16', 'bf16', 'fp32'], help="Precision to use for model inference", default=default_precision)
args = parser.parse_args()

if args.precision == "auto":
    free_mem_gb = get_cuda_free_memory_gb()
    
    if free_mem_gb > 60:
        # Experimental, we do not know if this really increases the quality of the results.
        target_precision = torch.float32
    elif torch.cuda.get_device_properties().major >= 8:
        target_precision = torch.bfloat16
    else:
        target_precision = torch.float16
elif args.precision == "bf16":
    target_precision = torch.bfloat16
elif args.precision == "fp16":
    target_precision = torch.float16
else:
    # Experimental, we do not know if this really increases the quality of the results.
    target_precision = torch.float32
    
print(f"Precision: {target_precision}")