"""Optional, read-only AST inspection of an installed ComfyUI native H3 module.

This checks public names/constants only. It never runs extracted source and
is not a native allocation or GPU parity test.
"""
import ast
import os
from pathlib import Path
import unittest

SOURCE = os.environ.get('COMFYUI_H3_SOURCE')


@unittest.skipUnless(SOURCE, 'Set COMFYUI_H3_SOURCE for read-only native source checks.')
class NativeSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tree = ast.parse(Path(SOURCE).read_text(encoding='utf-8'))

    def test_native_temporal_constants(self):
        constants = {}
        for item in self.tree.body:
            if isinstance(item, ast.Assign) and isinstance(item.value, ast.Constant):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        constants[target.id] = item.value.value
        self.assertEqual(constants.get('FPS'), 24)
        self.assertEqual(constants.get('AUDIO_LATENT_FPS'), 40)

    def test_native_empty_latent_public_arguments(self):
        node = next((item for item in self.tree.body
                     if isinstance(item, ast.ClassDef) and item.name == 'EmptyMiniMaxH3LatentAV'), None)
        self.assertIsNotNone(node, 'Native EmptyMiniMaxH3LatentAV is required.')
        method = next((item for item in node.body
                       if isinstance(item, ast.FunctionDef) and item.name == 'execute'), None)
        self.assertIsNotNone(method)
        names = {arg.arg for arg in method.args.args + method.args.kwonlyargs}
        self.assertTrue({'width', 'height', 'length'}.issubset(names))
