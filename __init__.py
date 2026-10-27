"""H3 Video Controller. Author: Aman Dolorain."""
from importlib import import_module
from .planning import FPS, PRESETS, make_plan

__author__ = 'Aman Dolorain'
__version__ = '1.0.0'
WEB_DIRECTORY = './web'


def _native_module():
    try:
        return import_module('comfy_extras.nodes_minimax_h3')
    except ImportError as error:
        raise RuntimeError('Native MiniMax H3 support is unavailable. Update ComfyUI and check '
                           'its startup errors. This pack does not install model dependencies.') from error


def _results(output, expected):
    result = getattr(output, 'result', None)
    if not isinstance(result, (tuple, list)) or len(result) != expected:
        raise RuntimeError('The native H3 output contract changed. Update this pack before running.')
    return result


def _check_latent(latent, plan):
    samples = latent.get('samples') if isinstance(latent, dict) else None
    tensors = getattr(samples, 'tensors', ())
    if (not getattr(samples, 'is_nested', False) or len(tensors) != 2
            or tuple(tensors[0].shape) != plan.video_shape
            or tuple(tensors[1].shape) != plan.audio_shape):
        raise RuntimeError('Native H3 latent dimensions differ from the timing plan. '
                           'No inconsistent metadata was returned. Check ComfyUI/pack compatibility.')


class H3VideoController:
    CATEGORY = 'ComfyUI/Video/H3/Control'
    DESCRIPTION = ('Author: Aman Dolorain. MiniMax H3 24 FPS timing, flexible resolution, '
                   'native joint AV latent, and optional native T2V/I2V preparation. '
                   'Use matching H3 models; this is not a sampler or a universal model adapter.')
    FUNCTION = 'prepare'
    RETURN_TYPES = ('LATENT', 'CONDITIONING', 'VHS_VIDEOINFO', 'INT', 'FLOAT', 'FLOAT',
                    'INT', 'INT', 'STRING')
    RETURN_NAMES = ('latent', 'positive', 'video_info', 'frame_count', 'fps',
                    'actual_duration_seconds', 'width', 'height', 'summary')

    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {
            'duration_seconds': ('FLOAT', {'default': 5.0, 'min': 0.01, 'max': 149.66, 'step': 0.1}),
            'width': ('INT', {'default': 512, 'min': 1, 'max': 16384, 'step': 1}),
            'height': ('INT', {'default': 512, 'min': 1, 'max': 16384, 'step': 1}),
            'resolution_preset': (list(PRESETS), {'default': 'Custom',
                'tooltip': 'Custom uses width/height. Other presets override both.'}),
            'size_rounding': (['nearest', 'down', 'up', 'exact'], {'default': 'nearest',
                'tooltip': 'H3 internally uses multiples of 32. Exact preserves a supported size.'}),
            'frame_rounding': (['up', 'nearest', 'down'], {'default': 'up',
                'tooltip': 'H3 frame grid is 17k+5 at fixed 24 FPS. Outputs report actual timing.'}),
            'prepare_mode': (['T2V / I2V', 'Empty AV latent'], {'default': 'T2V / I2V'}),
            'prompt': ('STRING', {'default': '', 'multiline': True,
                'tooltip': 'Describe scene, motion and audio. Used in T2V / I2V mode only.'}),
        }, 'optional': {
            'clip': ('CLIP', {'tooltip': 'Matching H3 text encoder; required in T2V / I2V mode.'}),
            'video_vae': ('VAE', {'tooltip': 'Matching H3 video VAE; required in T2V / I2V mode.'}),
            'first_frame': ('IMAGE', {'tooltip': 'Native H3 behavior stretches this image to the canvas.'}),
            'last_frame': ('IMAGE', {'tooltip': 'Native H3 behavior center-crops this image to the canvas.'}),
        }}

    def prepare(self, duration_seconds, width, height, resolution_preset='Custom',
                size_rounding='nearest', frame_rounding='up', prepare_mode='T2V / I2V',
                prompt='', clip=None, video_vae=None, first_frame=None, last_frame=None):
        plan = make_plan(duration_seconds, width, height, resolution_preset,
                         size_rounding, frame_rounding)
        if prepare_mode not in ('T2V / I2V', 'Empty AV latent'):
            raise ValueError('Unknown preparation mode.')
        if prepare_mode == 'T2V / I2V':
            if clip is None or video_vae is None:
                raise ValueError('T2V / I2V mode requires clip and video_vae. For a model-free '
                                 'latent/timing check choose Empty AV latent mode.')
        elif prompt.strip() or any(x is not None for x in (clip, video_vae, first_frame, last_frame)):
            raise ValueError('Empty AV latent mode does not process prompts or keyframes. '
                             'Use T2V / I2V mode, or clear these inputs.')
        native = _native_module()
        if prepare_mode == 'T2V / I2V':
            if not hasattr(native, 'MiniMaxH3ImageToVideo'):
                raise RuntimeError('This ComfyUI build lacks MiniMaxH3ImageToVideo. Update ComfyUI.')
            positive, latent = _results(native.MiniMaxH3ImageToVideo.execute(
                clip=clip, vae=video_vae, prompt=prompt, width=plan.width, height=plan.height,
                length=plan.frames, first_frame=first_frame, last_frame=last_frame), 2)
        else:
            if not hasattr(native, 'EmptyMiniMaxH3LatentAV'):
                raise RuntimeError('This ComfyUI build lacks EmptyMiniMaxH3LatentAV. Update ComfyUI.')
            latent, = _results(native.EmptyMiniMaxH3LatentAV.execute(
                width=plan.width, height=plan.height, length=plan.frames), 1)
            positive = None  # Intentionally unavailable; do not connect this output in Empty mode.
        _check_latent(latent, plan)
        summary = plan.summary() + '\nPreparation: ' + prepare_mode
        if positive is None:
            summary += '\nPositive output is unavailable in Empty AV latent mode.'
        return {'ui': {'text': [summary]}, 'result': (
            latent, positive, plan.video_info(), plan.frames, FPS, plan.actual_seconds,
            plan.width, plan.height, summary)}


NODE_CLASS_MAPPINGS = {'H3VideoController': H3VideoController}
NODE_DISPLAY_NAME_MAPPINGS = {'H3VideoController': 'H3 Video Controller'}
