import random
from pydantic import BaseModel, Field
from typing import Optional

class JobInputConfig(BaseModel):
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
    #selected_loras: list[str] = Field(default_factory=list)
    resolutionW: int = 640
    resolutionH: int = 640
    
class JobInputModel(BaseModel):
    name: str
    source: str
    weight: Optional[float] = 1.0

class JobInput(BaseModel):
    image_url: str
    loras: list[JobInputModel] = Field(default_factory=list)
    config: JobInputConfig