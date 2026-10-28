# Development — 1.2.0

planning.py preserves the existing H3 timing and resolution calculations.
__init__.py delegates allocation only to native EmptyMiniMaxH3LatentAV and checks its nested tensor shapes.
web/author.js uses the approved internal footer design with the H3 node identity.

Validation: 16 local unit tests pass; two optional current-native-source tests require COMFYUI_H3_SOURCE. JavaScript syntax passes Node module syntax checking. GPU generation and live ComfyUI frontend appearance have not been tested in this update.

The 1.2.0 output layout removes positive. Existing workflows must recreate the controller and reconnect outputs by name. See README.md for installation and wiring.
