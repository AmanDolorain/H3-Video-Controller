# H3 reference workflow

See README.md for current 1.1.0 inputs, outputs and upgrade steps.

Controller width → H3 reference connector width.
Controller height → H3 reference connector height.
Controller frame_count → H3 reference connector length.
Controller actual_duration_seconds → audio selection duration where supported.
Separate Simple Prompt STRING → H3 reference connector prompt.
CLIP, Video VAE, Audio VAE, reference images/video/audio → matching connector inputs.
Connector positive → guider conditioning.
Connector LATENT → sampler latent_image.

The controller no longer processes prompts or keyframes. Its latent output is empty and separate from the connector latent.
