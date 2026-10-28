"""Optional comparison against actual ComfyUI source without loading torch/models.

Set COMFYUI_H3_SOURCE to your ComfyUI/comfy_extras/nodes_minimax_h3.py.
Only the reviewed pure functions/native execute methods are extracted with AST.
"""
import ast
import math
import os
import pathlib
import types
import unittest
from test_control import MODULE, make_plan

SOURCE=os.environ.get('COMFYUI_H3_SOURCE')


@unittest.skipUnless(SOURCE, 'Set COMFYUI_H3_SOURCE for the native source contract checks.')
class NativeSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source=ast.parse(pathlib.Path(SOURCE).read_text())
        functions={'align_frame_count','video_latent_t','temporal_shape','_empty_av_latent'}
        chosen=[]
        for item in source.body:
            if isinstance(item,ast.FunctionDef) and item.name in functions: chosen.append(item)
            if isinstance(item,ast.ClassDef) and item.name in ('EmptyMiniMaxH3LatentAV','MiniMaxH3ImageToVideo'):
                item.bases=[]
                item.body=[x for x in item.body if isinstance(x,ast.FunctionDef) and x.name=='execute']
                chosen.append(item)
        class Output:
            def __init__(self,*args): self.result=args
        class Tensor:
            def __init__(self,shape): self.shape=shape
        class Nested:
            is_nested=True
            def __init__(self,tensors): self.tensors=tensors
        cls.resize_calls=[]
        ns={'FPS':24,'AUDIO_LATENT_FPS':40,'io':types.SimpleNamespace(NodeOutput=Output),
            'torch':types.SimpleNamespace(zeros=lambda shape,device:Tensor(tuple(shape))),
            'comfy':types.SimpleNamespace(model_management=types.SimpleNamespace(intermediate_device=lambda:'cpu'),
                                           nested_tensor=types.SimpleNamespace(NestedTensor=Nested)),
            '_resize':lambda image,w,h,crop: cls.resize_calls.append((w,h,crop)) or image,
            'node_helpers':types.SimpleNamespace(conditioning_set_values=lambda cond,values:[cond,values])}
        exec(compile(ast.fix_missing_locations(ast.Module(body=chosen,type_ignores=[])),str(SOURCE),'exec'),ns)
        cls.native=types.SimpleNamespace(**ns)

    def test_every_temporal_shape_matches_current_native_source(self):
        for frames in range(5,3593,17):
            p=make_plan(frames/24)
            actual=self.native.EmptyMiniMaxH3LatentAV.execute(p.width,p.height,p.frames).result[0]
            MODULE._check_latent(actual,p)
            self.assertEqual(self.native.temporal_shape(p.frames),(p.frames,p.video_shape[2],p.audio_shape[-1]))

    def test_all_resolutions_match_native_allocation(self):
        for w,h in ((512,512),(128,128),(854,479),(480,864),(3840,2160)):
            p=make_plan(width=w,height=h)
            actual=self.native.EmptyMiniMaxH3LatentAV.execute(p.width,p.height,p.frames).result[0]
            MODULE._check_latent(actual,p)

