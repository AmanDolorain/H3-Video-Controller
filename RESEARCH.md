# Source research and validation

Author: Aman Dolorain

Research date: 2026-10-27. The code delegates to the installed native implementation at runtime; it does not ship or replace the ComfyUI source.

## Native H3 source

Reviewed ComfyUI source revision `95539f56344958339e39b7582a476267d489b0ee` for `comfy_extras/nodes_minimax_h3.py`:

https://github.com/Comfy-Org/ComfyUI/blob/95539f56344958339e39b7582a476267d489b0ee/comfy_extras/nodes_minimax_h3.py

Verified these contracts:

- Fixed generation rate: 24 FPS.
- Canvas alignment: 32 pixels per side.
- Frame counts: 17k+5, minimum 5.
- Video latent shape: [1,24,2+5k,H/16,W/16].
- Audio latent shape: [1,32,2,round((frames/24)*40)].
- Joint samples are a native NestedTensor pair, not a single 16-channel tensor.
- Native T2V/I2V execute returns positive conditioning and the packed AV latent.
- First-frame guidance uses native stretch behavior; last-frame guidance uses native center crop.
- Native temporal documentation describes an approximately 5-15 second trained range.

The pure planner is compared with the native functions and execute methods in the optional source-contract tests. Each prepared latent is checked against the plan at runtime before metadata is returned.

## Official H3 documentation and workflows

https://docs.comfy.org/tutorials/video/minimax/minimax-h3-native

https://github.com/Comfy-Org/workflow_templates/blob/main/templates/video_minimax_h3_t2v.json

https://github.com/Comfy-Org/workflow_templates/blob/main/templates/video_minimax_h3_i2v.json

https://github.com/Comfy-Org/workflow_templates/blob/main/templates/video_minimax_h3_r2v.json

https://github.com/Comfy-Org/workflow_templates/blob/main/templates/video_minimax_h3_fun_controlnet_union.json

The sampled native graphs use RandomNoise, BasicGuider, KSamplerSelect, BasicScheduler and SamplerCustomAdvanced. R2V is a distinct conditioning path and is not claimed as a wrapped feature of this pack. Native H3 sampling outputs are sent to both the video VAE decoder and the audio VAE decoder.

512 x 512 satisfies the native canvas/latent grid. This verifies representability; actual generation quality, hardware fit and arbitrary-aspect checkpoint performance are not established by a dimension check.

## Frontend and Manager

https://github.com/Comfy-Org/ComfyUI_frontend/blob/main/src/renderer/extensions/vueNodes/components/LGraphNode.vue

https://github.com/Comfy-Org/ComfyUI_frontend/blob/main/src/renderer/extensions/vueNodes/components/NodeBadges.vue

https://github.com/Comfy-Org/ComfyUI-Manager/blob/main/glob/manager_core.py

https://github.com/Comfy-Org/ComfyUI-Manager/blob/main/glob/manager_server.py

The author credit attaches to the native Vue bottom badge row, with a classic canvas fallback. Manager Registry titles and installed canvas titles are separate data sources; cache refresh may delay a changed listing title.

## Publishing

https://docs.comfy.org/registry/publishing

https://docs.comfy.org/registry/specifications

The package includes the confirmed publisher ID `amandolorain`. The package ID must still be accepted by the Registry during first publication. No fake publisher ID, download counts, rating, verification badge or search-ranking guarantee is included.

The supplied checkout@v5 and setup-python@v6 action manifests were checked to use Node.js 24. Dependencies inside the external Registry publishing action are managed by that upstream action.

## Validation performed

All 21 Python checks passed with the reviewed native source available. These include 18 unit tests and three native-source contract tests, with lightweight substitutes for tensors and model services. Every supported temporal grid point and every integer dimension from 1 to 16384 were exercised.

The actual H3 pack's author extension was exercised in headless Chromium using a fixture reproducing the reviewed Vue body/badge-row structure. The checks cover shared row alignment, full author text, resize, hidden/restored badges, collapse/expand, cleanup and classic fallback positioning.

Full ComfyUI execution with real PyTorch, native model weights, text encoder, video/audio VAEs and a GPU has not been performed here. Those integration results must be established on the target system before treating the release as production-validated.
