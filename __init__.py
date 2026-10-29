"""H3 Video Controller. Author: Aman Dolorain."""
from importlib import import_module
from .planning import FPS, PRESETS, make_plan

__author__ = 'Aman Dolorain'
__version__ = '1.2.3'
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
    DESCRIPTION = ('MiniMax H3 timing, resolution and empty joint video/audio latent. '
                   'Connect width, height and frame_count to the separate H3 reference connector. '
                   'Author: Aman Dolorain.')
    FUNCTION = 'prepare'
    RETURN_TYPES = ('LATENT', 'VHS_VIDEOINFO', 'INT', 'FLOAT', 'FLOAT', 'INT', 'INT', 'STRING')
    RETURN_NAMES = ('latent', 'video_info', 'frame_count', 'fps', 'actual_duration_seconds',
                    'width', 'height', 'summary')

    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {
            'duration_seconds': ('FLOAT', {'default': 5.0, 'min': 0.01, 'max': 149.66, 'step': 0.1}),
            'fps': ('FLOAT', {'default': FPS, 'min': FPS, 'max': FPS, 'step': 1,
                'tooltip': 'MiniMax H3 native generation rate is fixed at 24 FPS.'}),
            'width': ('INT', {'default': 512, 'min': 1, 'max': 16384, 'step': 1}),
            'height': ('INT', {'default': 512, 'min': 1, 'max': 16384, 'step': 1}),
            'resolution_preset': (list(PRESETS), {'default': 'Custom',
                'tooltip': 'Custom uses width/height. Other presets override both.'}),
        }}

    def prepare(self, duration_seconds, width, height, resolution_preset='Custom',
                fps=FPS):
        if isinstance(fps, bool) or fps != FPS:
            raise ValueError('MiniMax H3 native generation requires 24 FPS.')
        plan = make_plan(duration_seconds, width, height, resolution_preset,
                         'nearest', 'up')
        native = _native_module()
        if not hasattr(native, 'EmptyMiniMaxH3LatentAV'):
            raise RuntimeError('This ComfyUI build lacks EmptyMiniMaxH3LatentAV. Update ComfyUI.')
        latent, = _results(native.EmptyMiniMaxH3LatentAV.execute(
            width=plan.width, height=plan.height, length=plan.frames), 1)
        _check_latent(latent, plan)
        summary = plan.summary() + '\nPreparation: Empty AV latent; prompt and references use the separate H3 connector.'
        return {'ui': {'text': [summary]}, 'result': (
            latent, plan.video_info(), plan.frames, FPS, plan.actual_seconds,
            plan.width, plan.height, summary)}


NODE_CLASS_MAPPINGS = {'H3VideoController': H3VideoController}
NODE_DISPLAY_NAME_MAPPINGS = {'H3VideoController': 'H3 Video Controller'}
