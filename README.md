<h1 align="center">FramePack Studio</h1>


[![Discord](https://img.shields.io/badge/Discord-%235865F2.svg?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/MtuM7gFJ3V)[![Patreon](https://img.shields.io/badge/Patreon-F96854?style=for-the-badge&logo=patreon&logoColor=white)](https://www.patreon.com/ColinU)

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/colinurbs/FramePack-Studio)

FramePack Studio is an AI video generation application based on FramePack that strives to provide everything you need to create high quality video projects. 

## Current Features

- **F1 and Original FramePack Models**: Run both in a single queue
- **End Frame Control for 'Original' Model**: Provides greater control over generations
- **Timestamped Prompts**: Define different prompts for specific time segments in your video
- **Prompt Blending**: Define the blending time between timestamped prompts
- **LoRA Support**: Works with most (all?) hunyuan LoRAs
- **Queue System**: Process multiple generation jobs without blocking the interface
- **Metadata Saving/Import**: Prompt and seed are encoded into the output PNG, all other generation metadata is saved in a JSON file
- **I2V and T2V**: Works with or without an input image to allow for more flexibility when working with standard LoRAs
- **Latent Image Options**: When using T2V you can generate based on a black, white, green screen or pure noise image

## Planned Features
- **Upscaling and Post-processing**
- **Generation Improvements**
- **Video Extension**
- **Audio Generation + TTS**
- **Lipsyncing**
- **Basic Editing**
- **Additional Models**


## Fresh Installation

### Prerequisites

- Python 3.10+
- CUDA-compatible GPU with at least 8GB VRAM (16GB+ recommended)
- 16GB System Memory (32GB+ strongly recommended) 

### Setup

Install via the Pinokio community script "FP-Studio" or:

1. Clone the repository:
   ```bash
   git clone https://github.com/colinurbs/FramePack-Studio.git
   cd FramePack-Studio
   ```

2. Install PyTorch:

   Go to the [PyTorch Getting Started](https://pytorch.org/get-started/locally/) page and install PyTorch according to your system setup.
   For example, if using CUDA 12.6 on Windows:
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
   ```

3. Install additional dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the studio interface:

```bash
python studio.py
```

Additional command line options:
- `--share`: Create a public Gradio link to share your interface
- `--server`: Specify the server address (default: 0.0.0.0)
- `--port`: Specify a custom port
- `--inbrowser`: Automatically open the interface in your browser
- `--offline`: Disable HF model checks to allow use without internet

## LoRAs

Add LoRAs to the /loras/ folder at the root of the installation. Select the LoRAs you wish to load and set the weights for each generation. Most Hunyuan LoRAs were originally trained for T2V, it's often helpful to run a T2V generation to ensure they're working before useing input impages.

NOTE: slow lora loading is a known issue

## Working with Timestamped Prompts

You can create videos with changing prompts over time using the following syntax:

```
[0s: A serene forest with sunlight filtering through the trees ]
[5s: A deer appears in the clearing ]
[10s: The deer drinks from a small stream ]
```

Each timestamp defines when that prompt should start influencing the generation. The system will (hopefully) smoothly transition between prompts for a cohesive video.

## Credits
Many thanks to [Lvmin Zhang](https://github.com/lllyasviel) for the absolutely amazing work on the original [FramePack](https://github.com/lllyasviel/FramePack) code!

Thanks to [Rickard Edén](https://github.com/neph1) for the LoRA code and their general contributions to this growing FramePack scene!

Thanks to everyone who has joined the Discord, reported a bug, sumbitted a PR or helped with testing!



    @article{zhang2025framepack,
        title={Packing Input Frame Contexts in Next-Frame Prediction Models for Video Generation},
        author={Lvmin Zhang and Maneesh Agrawala},
        journal={Arxiv},
        year={2025}
    }
