"""Pure H3 timing and resolution planning; no torch or model imports."""
from dataclasses import dataclass
import math

FPS = 24.0
MAX_DIMENSION = 16384
MAX_FRAMES = 3592  # Largest 17k+5 value not exceeding the native length limit 3600.
PRESETS = {
    'Custom': None,
    'Square 128 x 128': (128, 128),
    'Square 256 x 256': (256, 256),
    'Square 512 x 512': (512, 512),
    'Square 640 x 640': (640, 640),
    'Square 768 x 768': (768, 768),
    'Square 1024 x 1024': (1024, 1024),
    'Landscape 640 x 352': (640, 352),
    'Landscape 864 x 480': (864, 480),
    'Portrait 480 x 864': (480, 864),
    'Landscape 1344 x 768': (1344, 768),
    'Portrait 768 x 1344': (768, 1344),
    '1080p request 1920 x 1080': (1920, 1080),
    'UHD 4K request 3840 x 2160': (3840, 2160),
    'Portrait 4K request 2160 x 3840': (2160, 3840),
    'DCI 4K request 4096 x 2160': (4096, 2160),
}


def resolve_size(width, height, preset='Custom', rounding='nearest'):
    if preset not in PRESETS:
        raise ValueError('Unknown resolution preset.')
    if rounding not in ('nearest', 'down', 'up', 'exact'):
        raise ValueError('Unknown size rounding mode.')
    requested = PRESETS[preset] or (width, height)
    actual = []
    for label, number in zip(('width', 'height'), requested):
        if isinstance(number, bool) or not isinstance(number, int) or not 1 <= number <= MAX_DIMENSION:
            raise ValueError(f'{label} must be a whole number from 1 to {MAX_DIMENSION}.')
        if rounding == 'exact':
            if number % 32:
                raise ValueError(f'Exact {label} {number} is not supported. Use a multiple of 32 '
                                 'or choose automatic size rounding.')
            value = number
        elif rounding == 'nearest':
            value = ((number + 16) // 32) * 32
        elif rounding == 'down':
            value = number // 32 * 32
        else:
            value = (number + 31) // 32 * 32
        actual.append(max(32, value))
    return (*requested, *actual)


@dataclass(frozen=True)
class H3Plan:
    requested_seconds: float
    requested_width: int
    requested_height: int
    width: int
    height: int
    frames: int
    actual_seconds: float
    video_shape: tuple
    audio_shape: tuple
    frame_rounding: str
    size_rounding: str

    def video_info(self):
        values = dict(fps=FPS, frame_count=self.frames, duration=self.actual_seconds,
                      width=self.width, height=self.height)
        return {f'{prefix}_{key}': value for prefix in ('source', 'loaded')
                for key, value in values.items()}

    def summary(self):
        notes = []
        if self.frames < 124 or self.frames > 362:
            notes.append('Duration is outside the native node\'s documented ~5-15s training range.')
        if min(self.width, self.height) < 512:
            notes.append('Small canvas: valid dimensions are not a model-quality guarantee.')
        if self.width * self.height > 768 * 1344:
            notes.append('Canvas exceeds the native reference area; VRAM and quality are unverified.')
        return ('MiniMax H3 | 24 FPS | joint video + audio latent\n'
                f'Requested size: {self.requested_width}x{self.requested_height} | '
                f'Actual size: {self.width}x{self.height}\n'
                f'Requested duration: {self.requested_seconds:g}s | Frames: {self.frames}\n'
                f'Actual duration: {self.actual_seconds:.9f}s | '
                f'Difference: {self.actual_seconds-self.requested_seconds:+.9f}s\n'
                f'Frame rounding: {self.frame_rounding} | Size rounding: {self.size_rounding}\n'
                f'Video shape: {self.video_shape} | Audio shape: {self.audio_shape}\n'
                'Metadata describes the prepared clip, not post-processed output.\n'
                'Author: Aman Dolorain' + ('\nNotes: ' + ' '.join(notes) if notes else ''))


def make_plan(duration_seconds=5.0, width=512, height=512, preset='Custom',
              size_rounding='nearest', frame_rounding='up'):
    if isinstance(duration_seconds, bool):
        raise ValueError('Duration must be a positive finite number of seconds.')
    try:
        seconds = float(duration_seconds)
    except (TypeError, ValueError):
        raise ValueError('Duration must be a positive finite number of seconds.') from None
    if not math.isfinite(seconds) or not 0.01 <= seconds <= MAX_FRAMES / FPS:
        raise ValueError(f'Duration must be from 0.01 to {MAX_FRAMES/FPS:g} seconds.')
    rw, rh, w, h = resolve_size(width, height, preset, size_rounding)
    groups = (seconds * FPS - 5) / 17
    if frame_rounding == 'up':
        groups = math.ceil(groups - 1e-10)
    elif frame_rounding == 'down':
        groups = math.floor(groups + 1e-10)
    elif frame_rounding == 'nearest':
        groups = math.floor(groups + 0.5 + 1e-10)
    else:
        raise ValueError('Unknown frame rounding mode.')
    frames = max(0, groups) * 17 + 5
    if frames > MAX_FRAMES:
        raise ValueError('Rounded frame count exceeds the native length limit. Reduce duration.')
    video_t = 2 + ((frames - 5) // 17) * 5
    actual = frames / FPS
    audio_t = round(actual * 40)  # Native Python round, not half-up rounding.
    return H3Plan(seconds, rw, rh, w, h, frames, actual,
                  (1, 24, video_t, h // 16, w // 16), (1, 32, 2, audio_t),
                  frame_rounding, size_rounding)
