# 1.2.3 — 2026-10-29

- Replace the optional upstream-source execution test with passive AST checks.
- Use ordinary package imports in unit tests.
- Exclude development tests and GitHub workflows from Registry archives via .comfyignore.
- Preserve controller runtime behavior, sockets, timing, resolution synchronization and footer.
- Registry security review remains external; publish success is not Active status.

# 1.2.2

- Synchronize displayed width/height with the selected resolution preset.
- Preserve and restore custom dimensions; manual dimension edits switch to Custom.
- Retain automatic nearest supported size rounding and legacy workflow repair.

# 1.2.1

- Repair legacy widget values loaded by position (FPS 512, height Custom, invalid preset).
- Remove stale legacy inputs and rebuild invalid output layouts, disconnecting ambiguous old wires.
- Preserve the approved footer and current five controls.

# 1.2.0

- Show only duration_seconds, fps (fixed native 24), width, height and resolution_preset.
- Automatically align size to nearest supported multiple of 32 and round frames up to the H3 grid.
- Keep all eight 1.1.0 outputs and the approved footer unchanged.
- Recreate nodes loaded from old workflows to remove stale serialized sockets/widgets.

# Changelog

## 1.1.0

- Remove CLIP, video VAE, first/last frame and prompt inputs.
- Remove obsolete preparation mode and positive conditioning output.
- Preserve timing, resolution, metadata and native empty AV latent support.
- Match the approved internal footer: header color, title font, left-aligned ♪ Aman Dolorain with title inset.
- Output indices changed: add a fresh node and reconnect by name after upgrading.

# Changelog

## 1.0.0

- Add a separate MiniMax H3 control node with fixed 24 FPS and 17k+5 timing.
- Add custom dimensions, automatic rounding, exact mode and square/portrait/landscape presets.
- Support 512 x 512 exactly and report actual dimensions for rounded requests.
- Delegate packed AV latent and optional T2V/I2V preparation to native ComfyUI H3 nodes.
- Return synchronized planned metadata and verify both native tensor shapes.
- Include full author credit Aman Dolorain and Registry publisher metadata from the first release.
