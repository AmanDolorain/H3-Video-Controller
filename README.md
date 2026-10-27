# H3 Video Controller

**Author: Aman Dolorain · Version: 1.0.0**

Prepare MiniMax H3 video timing, flexible resolution and a **joint video + audio latent** in one control node. In T2V / I2V mode, this node also delegates prompt and keyframe preparation to ComfyUI's native H3 implementation.

[Connections](WORKFLOW_GUIDE.md) · [Publishing](PUBLISHING.md) · [Development and verification](DEVELOPMENT.md) · [Research](RESEARCH.md)

## What it does

- Enter duration in seconds; H3's native generation rate is fixed at **24 FPS**.
- Use custom dimensions in one-pixel increments or choose square, portrait or landscape presets.
- **512 x 512 is supported without rounding.** Other square presets include 128, 256, 640, 768 and 1024.
- Automatically align dimensions to H3's internal 32-pixel grid, or preserve a supported size with `exact`.
- Snap frame count to H3's **17k + 5** grid; report the actual duration.
- Build the packed H3 video/audio latent through the installed **native public H3 node**, rather than inventing a tensor layout.
- Return planned `VHS_VIDEOINFO`, FPS, frame count, actual dimensions and a readable summary.
- Show **Author: Aman Dolorain** at the bottom-right, alongside the native package badge in Vue Nodes 2.0; retain a classic canvas fallback.

This is a separate pack. It can coexist with ComfyUI-Video-Control and does not change that pack's registered node ID, settings or outputs.

## Requirements

Use a recent ComfyUI version containing `comfy_extras.nodes_minimax_h3`, `EmptyMiniMaxH3LatentAV` and `MiniMaxH3ImageToVideo`. For generation, install the matching H3 diffusion model, H3 text encoder, video VAE and audio VAE as described in the official templates. This pack does not download models, install PyTorch, monkey-patch H3 internals or call a hosted API.

Registration does not import the H3 runtime; execution reports a clear error if native H3 support is missing. Model capability, precision, GPU memory and generation quality remain properties of the selected model and ComfyUI setup.

## Installation

Manual: extract the ZIP so that `ComfyUI/custom_nodes/H3VideoController/__init__.py` exists. Restart ComfyUI and hard-refresh the browser with Ctrl+F5. Search **H3 Video Controller** in category **ComfyUI / Video / H3 / Control**.

Once the repository is created and these files are committed, its Git URL will be:

```text
https://github.com/AmanDolorain/H3-Video-Controller.git
```

Do not install both a ZIP copy and a Git copy. Registry publication and Manager availability are separate from preparing this package; see PUBLISHING.md. No repository or Registry release is claimed to have been created by this ZIP.

## Preparation modes

| Mode | Inputs and behavior |
| --- | --- |
| `T2V / I2V` (default) | Connect `clip` and `video_vae`. Enter a prompt. Optional first/last images are passed to native MiniMaxH3ImageToVideo. Returns positive conditioning and an H3 AV latent. No first/last image means native text-to-video preparation. |
| `Empty AV latent` | Model-free allocation/timing check through EmptyMiniMaxH3LatentAV. Clear the prompt and leave clip/VAE/images disconnected. `positive` is unavailable (`None`) and must not be connected to a guider. |

The mode does not choose or switch diffusion checkpoints. Use the matching T2V/I2V H3 checkpoint externally. Native R2V reference lists are **not wrapped in version 1.0.0**; continue using the native reference node for that task. This node does not combine first/last-frame and reference-to-video modes or add a model loader, sampler, audio decoder, mixer or lip-sync model.

## Resolution controls

`Custom` uses width and height. Every other preset overrides both fields. Preset labels show the **requested**, not necessarily generated, size.

| Mode | Behavior |
| --- | --- |
| `nearest` | Closest multiple of 32, ties upward |
| `down` | Round down each dimension, with an absolute minimum of 32 |
| `up` | Round up each dimension |
| `exact` | Preserve dimensions only if already supported; otherwise report an error |

Any positive integer from 1 to 16384 can be entered, but the generated canvas has a minimum of 32 pixels per side. This is an allocation limit, not a claim that every tiny canvas produces useful video. Rounding each side independently can slightly change aspect ratio.

| Requested | Mode | Actual canvas |
| --- | --- | --- |
| 512 x 512 | exact or automatic | 512 x 512 |
| 854 x 479 | nearest | 864 x 480 |
| 854 x 479 | down | 832 x 448 |
| 480 x 864 | exact | 480 x 864 |
| 3840 x 2160 | nearest | 3840 x 2176 |
| 1 x 1 | automatic | 32 x 32 |

4K presets are **canvas requests**, not a promise of native 4K generation quality or sufficient VRAM. 2160 is not divisible by 32, so exact UHD 4K requires a separate final resize/crop after decoding. Do not mislabel a 3840 x 2176 generated video as 3840 x 2160. Smaller resolution reduces latent size, but the large model and text encoder must still fit or offload successfully.

For I2V, native H3 stretches the first frame to the selected canvas and center-crops the last frame. This node preserves that behavior. Match the canvas aspect ratio to your input image or preprocess the image explicitly.

## Timing

At 24 FPS, a 5-second request contains 120 target frames. H3 accepts 5, 22, 39, ... frames. Default `up` selects **124 frames**, so the prepared duration is **5.166666667 seconds**. `nearest` also selects 124; `down` selects 107 (4.458333333 seconds).

Use `actual_duration_seconds`, not the requested value, for external timing. Native H3 generates video and audio jointly; an external audio generator is not required for its native sound. The audio latent uses 40 temporal steps per second with native Python rounding. The summary reports the actual shapes and duration difference.

The native source describes approximately 5-15 seconds as its trained range. The node reports a note for requests outside that range. Its representable frame cap is 3592, but that is not a tested long-generation guarantee. One video is prepared per run; batch-size controls are deliberately omitted.

## Outputs

| Output | Type | Destination |
| --- | --- | --- |
| latent | LATENT | SamplerCustomAdvanced.latent_image |
| positive | CONDITIONING | BasicGuider.conditioning in T2V / I2V mode only |
| video_info | VHS_VIDEOINFO | Nodes expecting this typed metadata |
| frame_count | INT | A matching frame-count input, if needed |
| fps | FLOAT | Final Create Video / Video Combine frame rate (24) |
| actual_duration_seconds | FLOAT | Other duration controls that must match |
| width, height | INT | Other resolution controls; these are actual dimensions |
| summary | STRING | Preview as Text |

Metadata describes the prepared clip, not a measurement of frames after interpolation, resizing or trimming. Update it when downstream processing changes the clip.

## Testing

```bash
python -m unittest discover -s tests -v
```

The standard run has 18 unit tests and three optional native-source tests that skip unless COMFYUI_H3_SOURCE is set. See DEVELOPMENT.md for the native-source comparison and frontend test evidence. Full model generation and your installed ComfyUI UI still require an integration test. This is not a promise of perfect audio/visual synchronization or face preservation.

## License

MIT. Copyright Aman Dolorain. See LICENSE.
