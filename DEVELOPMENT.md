# Development and verification

Author: Aman Dolorain

- `planning.py`: pure seconds/frame-grid, resolution, shape and metadata planning.
- `__init__.py`: legacy-compatible registration and calls to native public H3 execute methods.
- `web/author.js`: Vue footer-row credit with classic canvas fallback.
- `tests/test_control.py`: validation, presets, timing, metadata and mocked native-wrapper tests.
- `tests/test_upstream_contract.py`: optional AST comparison against actual native ComfyUI source.

## Native delegation

The public EmptyMiniMaxH3LatentAV and MiniMaxH3ImageToVideo nodes allocate the packed video/audio tensors. This pack does not copy the native implementation or manually construct a different NestedTensor. The preparation code unwraps the V3 NodeOutput.result tuple and checks the actual video and audio tensor shapes before returning metadata. A changed native shape contract produces an explicit compatibility error rather than a silent mismatch.

The native module is imported only when executing the controller. Defining/searching the node does not require model downloads or initialize a separate runtime.

## Tests

Run from this directory:

```bash
python -m unittest discover -s tests -v
```

There are 18 standard tests and three optional source-contract tests. To run all 21 against your own native source on Windows CMD:

```bat
set COMFYUI_H3_SOURCE=C:\path\to\ComfyUI\comfy_extras\nodes_minimax_h3.py
python -m unittest discover -s tests -v
```

On Linux/macOS:

```bash
COMFYUI_H3_SOURCE=/path/to/ComfyUI/comfy_extras/nodes_minimax_h3.py python -m unittest discover -s tests -v
```

Source-contract tests extract the reviewed functions and public execute methods with Python AST. Tensor allocation, image operations and CLIP/VAE services use test substitutes. These checks verify agreement with upstream logic without loading weights; they are not actual PyTorch, VAE or model-inference tests.

The standard tests exercise every custom integer size from 1 through 16384 in each automatic rounding mode, every supported 17k+5 frame count, square/portrait/4K presets, native-call arguments, missing inputs and rejection of inconsistent native shapes.

The footer is tested separately in a Chromium fixture based on the official Vue node/badge-row structure. Tests include shared badge-row alignment, resizing, hidden/restored badges, collapse/expand, duplicate protection, cleanup and classic fallback positions. A full installed ComfyUI UI test and model generation remain necessary.

## Adding or changing nodes

Keep the node ID H3VideoController and output order stable for saved workflows. Change display text independently. New feature inputs should have backwards-compatible defaults. Do not introduce a configurable generation FPS for H3 without corresponding model-level support. Add shape/temporal contract tests when updating to a new H3 implementation.
