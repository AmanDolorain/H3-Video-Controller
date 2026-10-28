# H3 Video Controller 1.2.0

Author: Aman Dolorain

Controls MiniMax H3 duration, resolution and frame rounding. Produces a native empty joint video/audio latent and timing metadata. Requires ComfyUI with native `EmptyMiniMaxH3LatentAV` support.

## Inputs

- duration_seconds
- fps: native H3 24 FPS (fixed)
- width, height
- resolution_preset


Size rounding is automatic nearest multiple of 32; frame count rounds up to the supported H3 frame grid. Neither rounding dropdown is shown.

H3 timing and size rules are unchanged from 1.0.0: fixed 24 FPS, frame grid 17k+5, dimensions aligned to 32. Use actual_duration_seconds when matching audio to the prepared clip.

## Outputs, in order

1. latent
2. video_info
3. frame_count
4. fps
5. actual_duration_seconds
6. width
7. height
8. summary

## Reference workflow

Connect width, height and frame_count to the separate MiniMax H3 Reference to Video connector's width, height and length. Connect the separate prompt STRING, CLIP, VAEs and references directly to that connector. Use the connector's positive and LATENT outputs for reference-conditioned sampling. The controller's latent is an independent empty latent; it does not contain reference conditioning.

## Upgrade from 1.0.0

Replace the complete H3VideoController folder and restart ComfyUI, then hard-refresh the browser. Back up your workflow, remove the old H3 controller and add a fresh H3 Video Controller. Reconnect by output name: removing positive shifts output socket indices. The old clip, video_vae, first_frame, last_frame, prompt, prepare_mode, size_rounding and frame_rounding inputs are removed. FPS is shown as fixed 24 because native H3 does not support a different generation FPS. Other controls retain their behavior.

## Branding

The internal bottom bar uses the node header color. White ♪ Aman Dolorain text copies the title font and left inset in the Vue frontend, matching the approved VideoControl footer. A classic canvas fallback is included.

## Validation

Run `python -m unittest discover -s tests -v`. Native-source checks are optional with COMFYUI_H3_SOURCE set. Full GPU generation and frontend appearance must be verified in the target ComfyUI installation.
