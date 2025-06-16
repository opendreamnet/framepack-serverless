# FP Studio User Guide

## Generate Tab

### Generation Types

The application offers several distinct methods for generating videos, each tailored to different use cases and input types.

- __Original__: This is the original FramePack image-to-video generation type. It takes an optional starting frame (an image) and a text prompt to generate a video. If no starting frame is provided, it uses a "latent image" (like a black or noise-filled frame) as the initial input. This model generates the video in reverse chronological order. It can struggle with creating dynamic motion but is generally better than F1 and maintaining consistency. 

- __Original with Endframe__: This type extends the "Original" method by allowing you to specify both a starting frame and an ending frame. The generation is guided by the prompt, but it will conclude on the provided end frame. This is useful for creating seamless loops or ensuring the video transitions to a specific final scene. 

- __F1__: F1 is a different implementation of the FramePack approach to video generation, while still based on Hunyuan video this model generates in chronologial order. F1 is generally better at creating dynamic motion but worse at maintaing consitency throughout a video. Additionally it tends to create a noticable 'pulse' between sections.

- __Video__: This generation type will extend the input video using the 'original' FramePack model. 

- __Video with Endframe__: Functionally similar to 'video' but allows for use of an endframe to guide the video extension.
  
- __Video F1__: Extends videos using the 'F1' model.

- __Grid__: This is a powerful utility for experimentation and comparison. It allows you to generate a grid of videos by systematically varying one or two parameters across the X and Y axes. For example, you can create a grid where each column has a different number of "Steps" and each row has a different "Distilled CFG Scale". This is invaluable for understanding how different parameters affect the final output without having to run each generation manually. After the individual generations complete they will be combined into a final video grid.

### Generation Parameters

These are the parameters available on the "Generate" screen. Many are shared across multiple generation types.

#### Core Inputs

- __Start Frame (optional)__

  - __Applies to__: `Original`, `Original with Endframe`, `F1`
  - An image that serves as the first frame of the generated video. If not provided, a latent image is used.

- __Video Input__

  - __Applies to__: `Video`, `Video with Endframe`, `Video F1`
  - The source video to be transformed.

- __End Frame (Optional)__

  - __Applies to__: `Original with Endframe`, `Video with Endframe`
  - An image that the generated video will conclude on.

- __End Frame Influence__

  - __Applies to__: `Original with Endframe`, `Video with Endframe`
  - A slider (0.05 to 1.0) that controls how strongly the end frame guides the generation. A value of 1.0 means full influence.

- __Latent Image__

  - __Applies to__: All types except `Grid` (when no Start Frame is provided).
  - The initial image to start generation from if no `Start Frame` is given. Options are typically `Black`, `White`, `Noise`, or `Green Screen`.

#### Prompting

- __Prompt__

  - __Applies to__: All types.
  - The text description of the desired video content. You can use timestamps (e.g., `[2s: a person is smiling]`) to guide the animation over time.

- __Negative Prompt__

  - __Applies to__: All types except `Grid`.
  - Describes what you *don't* want to see in the video, helping to steer the generation away from undesired elements or styles.

- __Number of sections to blend between prompts__

  - __Applies to__: All types except `Grid`.
  - Controls the smoothness of transitions between different timestamped sections in your prompt. A higher value creates more gradual blending.

#### Generation Settings

- __Steps__

  - __Applies to__: All types.
  - The number of denoising steps the model takes to generate each frame. More steps can increase detail but will take longer.

- __Video Length (Seconds)__

  - __Applies to__: All types.
  - The desired duration of the output video.

- __Resolution (Width & Height)__

  - __Applies to__: All types.
  - The dimensions of the output video. The system will automatically select the nearest supported "bucket" size.

- __Seed__

  - __Applies to__: All types.
  - A number that initializes the random noise pattern for generation. Using the same seed with the same parameters will produce a nearly identical output.

- __Randomize__

  - __Applies to__: All types.
  - If checked, a new random seed will be used for each generation job.

#### Advanced Parameters

- __Use TeaCache__

  - __Applies to__: All types.
  - Enables a caching mechanism (`TeaCache`) that can significantly speed up generation, though it may slightly degrade the quality of fine details like hands.

- __TeaCache steps__

  - __Applies to__: All types (when `Use TeaCache` is enabled).
  - The number of intermediate steps to keep in the cache.

- __TeaCache rel_l1_thresh__

  - __Applies to__: All types (when `Use TeaCache` is enabled).
  - A threshold that determines how much change is needed between frames to invalidate the cache.

- __Distilled CFG Scale__

  - __Applies to__: All types.
  - Controls how closely the generation adheres to the prompt. Higher values mean stronger adherence.

- __Combine with source video__

  - __Applies to__: `Video`, `Video with Endframe`, `Video F1`
  - If checked, the generated video will be blended with the original source video.

- __Number of Context Frames (Adherence to Video)__

  - __Applies to__: `Video`, `Video with Endframe`, `Video F1`
  - Controls how many frames from the source video are considered when generating a new frame. Higher values retain more detail from the source but are more computationally expensive and can sometimes restrict motion too much.

#### LoRAs & Metadata

- __Select LoRAs to Load__

  - __Applies to__: All types except `Grid`.
  - A dropdown to select one or more LoRA (Low-Rank Adaptation) models to apply during generation. LoRAs are small files that can modify the style or content of the output.

- __LoRA Weight Sliders__

  - __Applies to__: All types except `Grid`.
  - Individual sliders appear for each selected LoRA, allowing you to control the strength of its effect.

- __Upload Metadata JSON__

  - __Applies to__: All types except `Grid`.
  - Allows you to load all generation parameters from a previously saved JSON file, making it easy to replicate a past generation.


## Queue Tab

The "Queue" tab is where you can monitor and manage all of your video generation jobs. When you click "Add to Queue" on the Generate tab, your job is sent here. This allows you to line up multiple video generations to run one after another, creating an efficient, automated workflow.

---

#### __The Job Queue Table__

The central feature of this tab is the data table, which provides a real-time overview of all your jobs. Each row represents a single generation job and contains the following information:

- __Job ID__: A unique identifier for the job.

- __Type__: The generation type used for the job (e.g., `Original`, `Video`, `F1`).

- __Status__: The current state of the job.

  - `PENDING`: The job is waiting in the queue to be processed.
  - `RUNNING`: The job is currently being generated.
  - `COMPLETED`: The job finished successfully.
  - `FAILED`: The job stopped due to an error.
  - `CANCELLED`: The job was manually stopped by the user.

- __Created__: The timestamp when the job was added to the queue.

- __Started__: The timestamp when the job began processing.

- __Completed__: The timestamp when the job finished.

- __Elapsed__: The total time taken to process the job, from start to finish.

- __Preview__: A small thumbnail of the job's input image or video for easy identification.

---

#### __Queue Management Actions__

A set of powerful tools is available to help you manage the queue effectively:

- __Refresh Queue__: Manually updates the job list to show the most current status for all jobs.

- __Cancel Queue__: Cancels all jobs that are currently in the `PENDING` state. This will not affect a job that is already `RUNNING`. You will be asked to confirm this action.

- __Clear Complete__: Removes all jobs from the list that have a `COMPLETED`, `FAILED`, or `CANCELLED` status. This is useful for cleaning up the view to only show pending and running jobs.

- __Load Queue__: Loads the default `queue.json` file from your application directory. This is useful for restoring a queue from a previous session.

- __Export Queue__: Saves the current job list and all associated input images/videos into a single `.zip` file. This is perfect for moving a set of jobs to another computer or for archiving your work.

- __Import Queue__: Allows you to upload a `.json` or `.zip` file to add jobs to your queue. This is the corresponding action to `Export Queue` and is great for loading archived jobs or work from another user.


## Outputs Tab

#### __Key Components__

- __Video Gallery__

  - __What it is__: The main area of the tab is a gallery of thumbnails. Each thumbnail represents a unique video generation.
  - __Organization__: The gallery is automatically sorted with your most recently created videos appearing first, making it easy to find your latest work.

- __Video Player__

  - __How it works__: When you click on any thumbnail in the gallery, the full video is loaded into this player.
  - __Features__: The player includes standard controls to play, pause, and loop the video, allowing for a detailed review of the final output.

- __Generation Info__

  - __What it is__: A text box that displays the complete set of parameters (the "metadata") used to create the selected video.
  - __Content__: This includes the exact prompt, seed, model type, number of steps, and any other settings you used. This information is invaluable for understanding how a specific result was achieved and for replicating or iterating on that result later.

---

#### __Available Actions__

- __Refresh Button__

  - __Purpose__: If you have generations running in the background, they won't appear in the gallery until they are complete. Clicking the "Refresh" button will rescan your output folders and update the gallery with any newly finished videos.

- __➡️ Send to Post-processing Button__

  - __Purpose__: This powerful feature provides a seamless workflow for improving your generated videos.
  - __How it works__: After selecting a video from the gallery, clicking this button will send it directly to the __Post-processing__ tab. This allows you to immediately start tasks like upscaling the video to a higher resolution or using frame interpolation (like RIFE) to make the motion smoother, without having to manually find and upload the file again.

## Post Processing Tab

The "Post-processing" tab is a powerful suite of tools designed to enhance, refine, and transform your generated videos. You can send videos here directly from the "Outputs" tab or upload them manually. This tab allows you to chain multiple effects together for advanced editing workflows.

---

#### __Core Workflow & Interface__

- __Input & Output Players__:

  - __Upload Video (Top-Left)__: This is the primary input for all operations. Videos you send from the "Outputs" tab will appear here.
  - __Processed Video (Top-Right)__: The result of any operation you perform will be displayed in this player.

- __Chaining Operations__:

  - To apply multiple effects (e.g., upscale, then add filters), you can create a workflow:

    1. Perform the first operation.
    2. Once the result appears in the "Processed Video" player, click the __"🔄 Use Processed as Input"__ button.
    3. This moves your processed video to the input player, ready for the next operation.

- __Saving__:

  - __Autosave__: By default, all processed videos are automatically saved to a permanent folder.
  - __Manual Save__: You can disable the "Autosave" checkbox to have more control. When disabled, a __"💾 Save to Permanent Folder"__ button appears, allowing you to save the video in the "Processed Video" player on demand.

---

#### __Available Operations__

The tools are organized into tabs for easy access:

##### __📈 Upscale Video (ESRGAN)__

This tool increases the resolution of your video, making it sharper and more detailed.

- __ESRGAN Model__: Select from a list of pre-trained AI models, each designed for different types of content (e.g., animation, realistic video). The model's default output scale (e.g., 2x, 4x) will be displayed.
- __Tile Size__: To manage memory usage on large videos, you can process the video in smaller tiles. "Auto" is recommended, but smaller tile sizes (e.g., 512px) can prevent out-of-memory errors at the cost of slower processing.
- __Enhance Faces (GFPGAN)__: A secondary AI model that can be enabled to specifically detect and restore faces, often resulting in much clearer and more natural-looking features.

##### __🎨 Video Filters (FFmpeg)__

Apply a wide range of visual adjustments to your video.

- __Filter Sliders__: A collection of sliders to control:

  - __Color__: Brightness, Contrast, Saturation, Color Temperature.
  - __Clarity__: Sharpen, Blur, Denoise.
  - __Artistic Effects__: Vignette (darkens corners), S-Curve Contrast (subtle, cinematic contrast), Film Grain.

- __Presets__: You can save and load your favorite combination of filter settings.

  - Select a preset from the __"Load Preset"__ dropdown.
  - To save your current slider settings, type a name in the __"Preset Name"__ box and click __"💾 Save/Update"__.

##### __🎞️ Frame Adjust (Speed & Interpolation)__

Modify the speed and smoothness of your video.

- __RIFE Frame Interpolation__: Use AI to generate new frames *between* the existing ones. Selecting "2x RIFE Interpolation" will double the video's frame rate, resulting in significantly smoother motion.
- __Adjust Video Speed Factor__: Slow down (< 1.0) or speed up (> 1.0) the video playback.

##### __🔄 Video Loop__

Create seamless loops from your video clips.

- __Loop Type__:

  - `loop`: Plays the video from start to finish, then immediately starts again from the beginning.
  - `ping-pong`: Plays the video forward, then plays it in reverse to create a back-and-forth effect.

- __Number of Loops__: Control how many times the video repeats.

##### __🖼️ Frames I/O (Input/Output)__

This section gives you direct control over the individual frames of your video.

- __Extract Frames__:

  - Break down the input video into a sequence of individual image files (e.g., PNGs).
  - You can choose to extract every single frame or every Nth frame (e.g., every 5th frame).
  - Extracted frames are saved into their own uniquely named folder.

- __Reassemble Frames__:

  - Create a video *from* a folder of images.
  - You can select a folder you previously extracted or upload your own set of frames.
  - This is extremely useful for workflows where you might want to edit individual frames in an external program before turning them back into a video.

---

#### __System & File Management__

- __📤 Unload Studio Model__: Frees up significant video memory (VRAM) by unloading the main video generation model. This is highly recommended before running memory-intensive tasks like upscaling. The model will be reloaded automatically the next time you generate a video on the "Generate" tab.
- __📁 Open Output Folder__: Opens the folder where your permanently saved videos are stored.
- __🗑️ Clear Temporary Files__: Deletes all files from the temporary processing folder to free up disk space.

## Settings Tab

The "Settings" tab allows you to customize the application's behavior, file paths, and default parameters. Changes made here are saved to a `settings.json` file and will persist between sessions.

---

#### __Core Generation Settings__

These settings control the default values and behavior for video generation.

- __Save Metadata__

  - __Description__: When enabled, a JSON file is saved alongside every generated video. This file contains all the parameters used for that generation (prompt, seed, model, etc.), making it easy to replicate or analyze your results later.

- __GPU Inference Preserved Memory (GB)__

  - __Description__: A crucial setting for managing video memory (VRAM). It tells the application to keep a certain amount of VRAM free during generation.
  - __Usage__: If you encounter "Out of Memory" (OOM) errors, __increase__ this value. This will make generation slightly slower but more stable. If you have a powerful GPU and are not getting errors, you can decrease it for a potential speed boost.

- __MP4 Compression (CRF)__

  - __Description__: Controls the quality and file size of the final MP4 video. CRF stands for Constant Rate Factor.
  - __Usage__: A __lower__ value results in __higher quality__ and a larger file size. A __higher__ value results in __lower quality__ and a smaller file size. A value of `0` is lossless (very large file). A good range for high quality is typically `16-23`.

- __Clean up video files__

  - __Description__: During some generation processes, intermediate video files might be created. If this is checked, only the final, completed video will be kept, and all temporary video files will be deleted automatically.

---

#### __System Prompt (Advanced)__

This section allows for advanced customization of the underlying prompt structure for certain models.

- __Override System Prompt__

  - __Description__: When checked, the application will use the custom template you provide below instead of the model's default internal prompt structure. __This is an advanced feature and should generally be left unchecked unless you know what you are doing.__

- __System Prompt Template__

  - __Description__: The text box where you can define the custom prompt template. It requires a specific JSON format and is only recommended for expert users experimenting with model behavior.

---

#### __File & Directory Paths__

This is where you tell the application where to find and save files.

- __Output Directory__: The default folder where your final generated videos will be saved.
- __Metadata Directory__: The default folder where the metadata `.json` files will be saved.
- __LoRA Directory__: The folder where the application will look for your LoRA model files to populate the dropdown on the "Generate" tab.
- __Gradio Temporary Directory__: The path where the user interface framework (Gradio) stores temporary files, such as uploads.

---

#### __Application Settings__

General settings for the application's user interface and behavior.

- __Auto-save settings__

  - __Description__: When enabled, any changes you make on this settings page are saved automatically. If you disable this, you must click the "Save Settings" button to apply your changes.

- __Theme__

  - __Description__: Customizes the visual appearance of the user interface. You can choose from several themes (e.g., `soft`, `glass`, `mono`).
  - __Note__: A restart of the application is required for theme changes to take full effect.

---

#### __Actions__

- __Save Settings__: Manually saves all the current settings on the page to your `settings.json` file.
- __Clean Up Temporary Files__: Manually clears out the Gradio temporary directory. This can be useful to free up disk space if you've uploaded many large files.

