# Manual connections

Author: Aman Dolorain

## 1. Check timing and square resolution without loading model weights

Add H3 Video Controller and Preview as Text. Select `prepare_mode = Empty AV latent`, clear the prompt, and leave clip, video_vae, first_frame and last_frame disconnected. Set duration 5, width 512, height 512, preset Custom, size rounding nearest, frame rounding up.

Connect `summary` to Preview as Text and run. This requires the native H3 module but does not load model weights. It still allocates small empty video/audio tensors using ComfyUI's device configuration.

Expected summary:

- Requested and actual size: 512 x 512.
- Frames: 124; FPS: 24; actual duration: 124/24 seconds.
- Video latent: (1, 24, 37, 32, 32).
- Audio latent: (1, 32, 2, 207).

The positive output is unavailable in this mode. Do not connect it to a guider.

## 2. Prepare T2V / I2V

Switch to T2V / I2V. Use the model/precision combination appropriate for your hardware from an official H3 template.

| Source | Destination |
| --- | --- |
| H3-compatible CLIP Loader, type `minimax`, CLIP output | H3 controller `clip` |
| Matching H3 video VAE loader, VAE output | H3 controller `video_vae` |
| Load Image IMAGE, optional | `first_frame` |
| Second Load Image IMAGE, optional | `last_frame` |

Write the scene, camera, action and desired audio in the controller prompt. Do not also insert a separate H3ImageToVideo node for this T2V/I2V path: this controller delegates to it internally.

## 3. Sampling group

Add **RandomNoise**, **BasicGuider**, **KSamplerSelect**, **BasicScheduler** and **SamplerCustomAdvanced**.

| Source | Destination |
| --- | --- |
| Final H3 MODEL (after any appropriate model patches) | BasicGuider.model AND BasicScheduler.model |
| Controller positive | BasicGuider.conditioning |
| BasicGuider GUIDER | SamplerCustomAdvanced.guider |
| RandomNoise NOISE | SamplerCustomAdvanced.noise |
| KSamplerSelect SAMPLER | SamplerCustomAdvanced.sampler |
| BasicScheduler SIGMAS | SamplerCustomAdvanced.sigmas |
| Controller latent | SamplerCustomAdvanced.latent_image |

The sampled H3 templates use res_multistep. Step count depends on base versus the matching distilled/Lightning checkpoint and LoRA. Do not apply a generic 4-step, 8-step or CFG recommendation to every H3 model. This controller neither selects nor installs those weights.

## 4. Decode both streams and save

| Source | Destination |
| --- | --- |
| SamplerCustomAdvanced.output | VAE Decode.samples AND VAE Decode Audio.samples |
| Matching H3 video VAE | VAE Decode.vae |
| Matching H3 audio VAE | VAE Decode Audio.vae |
| VAE Decode IMAGE | Create Video.images |
| VAE Decode Audio AUDIO | Create Video.audio |
| Controller fps | Create Video.fps |
| Create Video VIDEO | Save Video.video |

Both decoders read the same packed AV latent and extract their own stream. Do not connect the audio VAE to the video decoder. The video VAE passed into the controller should also decode the video stream.

Do not add a separate music generator, TTS mixer or lip-sync model merely to make native H3 audio exist. Those are optional separate processing tasks and require a deliberate timing plan.

## 5. Test progressively

Start with timing/latent preview, then one small-square T2V/I2V generation using a verified matching H3 model stack. Confirm decoded frame count, resolution and audio duration before adding references or post-processing. A valid 512 x 512 tensor is not proof that a particular checkpoint runs well at that size. If you change playback FPS or interpolate frames later, update the output timing/metadata.
