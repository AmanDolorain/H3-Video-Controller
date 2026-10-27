import importlib.util
import math
import pathlib
import sys
import types
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('h3_video_controller', ROOT / '__init__.py',
                                             submodule_search_locations=[str(ROOT)])
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
from h3_video_controller.planning import make_plan, resolve_size, PRESETS, FPS, MAX_FRAMES


def latent_for(plan):
    return {'samples': types.SimpleNamespace(is_nested=True, tensors=(
        types.SimpleNamespace(shape=plan.video_shape), types.SimpleNamespace(shape=plan.audio_shape)))}


class PlanningTests(unittest.TestCase):
    def test_square_512_and_default_timing(self):
        p = make_plan()
        self.assertEqual((p.width, p.height), (512, 512))
        self.assertEqual(p.frames, 124)
        self.assertAlmostEqual(p.actual_seconds, 124/24)
        self.assertEqual(p.video_shape, (1, 24, 37, 32, 32))
        self.assertEqual(p.audio_shape, (1, 32, 2, 207))

    def test_square_presets_remain_square(self):
        for name, size in PRESETS.items():
            if name.startswith('Square'):
                p = make_plan(preset=name, width=1, height=13)
                self.assertEqual((p.width, p.height), size)
                self.assertEqual(p.width, p.height)

    def test_custom_rounding_and_portrait(self):
        expected = {'nearest': (864, 480), 'up': (864, 480), 'down': (832, 448)}
        for mode, size in expected.items():
            p = make_plan(width=854, height=479, size_rounding=mode)
            self.assertEqual((p.width, p.height), size)
            self.assertEqual((p.requested_width, p.requested_height), (854, 479))
        p = make_plan(width=480, height=864, size_rounding='exact')
        self.assertEqual(p.video_shape[-2:], (54, 30))

    def test_exact_does_not_silently_resize(self):
        self.assertEqual(resolve_size(512,512,rounding='exact'), (512,512,512,512))
        with self.assertRaisesRegex(ValueError, 'Exact'):
            resolve_size(854,480,rounding='exact')

    def test_4k_request_reports_aligned_actual_dimensions(self):
        p = make_plan(preset='UHD 4K request 3840 x 2160')
        self.assertEqual((p.requested_width,p.requested_height),(3840,2160))
        self.assertEqual((p.width,p.height),(3840,2176))
        self.assertIn('VRAM', p.summary())

    def test_all_pixel_inputs_and_boundary_modes(self):
        for n in range(1,16385):
            for mode in ('nearest','down','up'):
                _,_,w,h = resolve_size(n,n,rounding=mode)
                self.assertTrue(32 <= w <= 16384)
                self.assertEqual(w%32,0)
                self.assertEqual(w,h)
                if mode=='nearest': self.assertLessEqual(abs(w-n),max(16,32-n))
                if mode=='down' and n>=32: self.assertLessEqual(w,n)
                if mode=='up': self.assertGreaterEqual(w,n)

    def test_frame_modes(self):
        self.assertEqual(make_plan(5,frame_rounding='up').frames,124)
        self.assertEqual(make_plan(5,frame_rounding='nearest').frames,124)
        self.assertEqual(make_plan(5,frame_rounding='down').frames,107)
        self.assertEqual(make_plan(.01).frames,5)
        self.assertEqual(make_plan(1).frames,39)
        self.assertEqual(make_plan(1,frame_rounding='nearest').frames,22)

    def test_every_valid_frame_count_and_metadata(self):
        for frames in range(5,MAX_FRAMES+1,17):
            for mode in ('up','down','nearest'):
                p=make_plan(frames/FPS,frame_rounding=mode)
                self.assertEqual(p.frames,frames)
                self.assertEqual(p.video_shape[2],2+(frames-5)//17*5)
                self.assertEqual(p.audio_shape[-1],round(frames/FPS*40))
                info=p.video_info()
                self.assertEqual(len(info),10)
                self.assertEqual(info['loaded_duration'],p.actual_seconds)
                self.assertEqual(info['source_fps'],24.)

    def test_invalid_values(self):
        for kwargs in (dict(duration_seconds=0),dict(duration_seconds=float('inf')),
                       dict(duration_seconds=True),dict(duration_seconds=150),
                       dict(width=0),dict(height=-1),dict(width=True),dict(width=512.5),
                       dict(width=16385),dict(preset='typo'),dict(size_rounding='typo'),
                       dict(frame_rounding='typo')):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError): make_plan(**kwargs)


class WrapperTests(unittest.TestCase):
    def args(self, **kwargs):
        args=dict(duration_seconds=5,width=512,height=512)
        args.update(kwargs)
        return args

    def test_no_runtime_import_at_registration(self):
        fields=MODULE.H3VideoController.INPUT_TYPES()
        self.assertEqual(fields['required']['width'][1]['step'],1)
        self.assertEqual(MODULE.NODE_DISPLAY_NAME_MAPPINGS['H3VideoController'],'H3 Video Controller')
        self.assertEqual(MODULE.__author__,'Aman Dolorain')

    def test_missing_models_fail_before_native_import(self):
        with patch.object(MODULE,'_native_module') as load:
            with self.assertRaisesRegex(ValueError,'requires clip and video_vae'):
                MODULE.H3VideoController().prepare(**self.args())
            load.assert_not_called()

    def test_empty_mode_rejects_silently_ignored_inputs(self):
        for kw in (dict(prompt='hello'),dict(first_frame=object()),dict(clip=object())):
            with self.assertRaisesRegex(ValueError,'does not process'):
                MODULE.H3VideoController().prepare(**self.args(prepare_mode='Empty AV latent',**kw))

    def test_empty_mode_contract(self):
        p=make_plan()
        fake=types.SimpleNamespace(EmptyMiniMaxH3LatentAV=types.SimpleNamespace(
            execute=lambda **kw: types.SimpleNamespace(result=(latent_for(p),))))
        with patch.object(MODULE,'_native_module',return_value=fake):
            out=MODULE.H3VideoController().prepare(**self.args(prepare_mode='Empty AV latent'))['result']
        self.assertEqual(len(out),len(MODULE.H3VideoController.RETURN_TYPES))
        self.assertIsNone(out[1])
        self.assertEqual(out[3:5],(124,24.))
        self.assertEqual(out[6:8],(512,512))
        self.assertIn('unavailable',out[-1])

    def test_native_i2v_receives_actual_size_and_keyframes(self):
        p=make_plan(width=854,height=479)
        calls=[];clip=object();vae=object();first=object();last=object();positive=object()
        def execute(**kw):
            calls.append(kw)
            return types.SimpleNamespace(result=(positive,latent_for(p)))
        fake=types.SimpleNamespace(MiniMaxH3ImageToVideo=types.SimpleNamespace(execute=execute))
        with patch.object(MODULE,'_native_module',return_value=fake):
            out=MODULE.H3VideoController().prepare(**self.args(width=854,height=479,
                clip=clip,video_vae=vae,first_frame=first,last_frame=last,prompt='Scene. Audio.'))['result']
        self.assertEqual((calls[0]['width'],calls[0]['height'],calls[0]['length']),(864,480,124))
        self.assertIs(calls[0]['first_frame'],first);self.assertIs(calls[0]['last_frame'],last)
        self.assertIs(out[1],positive)
        self.assertEqual(out[2]['loaded_width'],864)

    def test_changed_native_layout_fails_instead_of_wrong_metadata(self):
        bad=latent_for(make_plan(width=256,height=256))
        fake=types.SimpleNamespace(EmptyMiniMaxH3LatentAV=types.SimpleNamespace(
            execute=lambda **kw: types.SimpleNamespace(result=(bad,))))
        with patch.object(MODULE,'_native_module',return_value=fake):
            with self.assertRaisesRegex(RuntimeError,'dimensions differ'):
                MODULE.H3VideoController().prepare(**self.args(prepare_mode='Empty AV latent'))

    def test_wrong_public_output_contract(self):
        with self.assertRaisesRegex(RuntimeError,'contract changed'):
            MODULE._results(types.SimpleNamespace(result=()),1)

    def test_missing_native_classes(self):
        with patch.object(MODULE,'_native_module',return_value=types.SimpleNamespace()):
            with self.assertRaisesRegex(RuntimeError,'lacks Empty'):
                MODULE.H3VideoController().prepare(**self.args(prepare_mode='Empty AV latent'))

    def test_unknown_mode(self):
        with self.assertRaisesRegex(ValueError,'Unknown preparation'):
            MODULE.H3VideoController().prepare(**self.args(prepare_mode='typo'))


if __name__ == '__main__': unittest.main()
