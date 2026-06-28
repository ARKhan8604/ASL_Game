# Avatar preview — procedural ASL sign on the robot avatar

A small proof-of-concept that drives **your `D:\robot.blend`** to perform an ASL sign in the
browser, using the **same Sign Definition Schema** the recognition engine uses (`signs/*.py`).
This is the "expressive avatar" side of the paper's pipeline, scoped down to one sign.

Currently implemented: **HELP** (`signs/help.py`).

## Files
- `build_help_glb.py` — headless Blender script. Rigs the robot's arms with a rigid
  empty-joint hierarchy (shoulder→elbow→wrist), parents the existing body-part meshes to it
  (no weight painting), solves the arm poses with an **analytical 2-bone IK solver**
  (Law of Cosines + pole vector, per the paper's Phase 4), keyframes the HELP motion, decimates
  for the web, and exports `robot_help.glb`.
- `robot_help.glb` — generated output (~7.5 MB). Don't edit by hand; regenerate.
- `help.html` — Three.js viewer. Loads the GLB, plays the clip with `AnimationMixer`, shows the
  HELP schema, and has speed / loop / camera controls.
- `emergency.html` — earlier primitive-hand experiment (no avatar). Kept for reference only.

## Rebuild the animation
```
"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" --background --python build_help_glb.py
```
Tune the sign by editing the wrist targets at the top of `build_help_glb.py`
(`TARGETS_TOGETHER`, `TARGETS_LIFTED`, `POLE`) — these are in Blender world space
(+X right, −Y front, +Z up). The IK solves the joint rotations for you.

## Run the viewer
GLTF must be served over http (not `file://`):
```
python -m http.server 8778 --directory .
```
then open http://127.0.0.1:8778/help.html

## Handshape note
The robot has no finger bones. The dominant **fist** is produced by baking a curl into the
sub-knuckle finger geometry of the right hand (`make_fist()` in `build_help_glb.py`,
controlled by `FIST_KNUCKLE_Z` / `FIST_PIVOT` / `FIST_ANGLE`). The non-dominant hand stays
open as the platform. So all four HELP parameters read correctly now: closed fist resting on
open palm, at center, lifting up.

## Honest caveats
- The fist is a baked geometry curl, not articulated finger joints — it's a good silhouette
  approximation, not anatomically exact.
- This pose is **uncalibrated**. Per the paper's Phase 6, a fluent/Deaf signer should review and
  adjust the schema targets before this is used as a real teaching reference.
- For a *single* sign, a recorded human clip is still the most accurate option. This pipeline
  earns its keep only when synthesizing a large vocabulary — exactly what the paper's Phase 9
  "sequencing reality check" recommends deferring until the core loop is proven.
