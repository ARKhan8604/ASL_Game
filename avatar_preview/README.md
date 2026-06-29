# Avatar preview — procedural ASL sign (HELP)

A proof-of-concept that drives a rigged avatar to perform an ASL sign in the browser, posed
directly from the **same Sign Definition Schema** the recognition engine uses (`signs/*.py`).
This is the "expressive avatar" side of the paper's pipeline, scoped to one sign.

## Current build — VRM avatar (recommended)
- **`help.html`** — loads the VRM humanoid with `@pixiv/three-vrm` and poses it procedurally at
  runtime. The avatar performs **HELP**: dominant **fist** rests on the open non-dominant palm,
  then both hands **lift up**.
- **`1895101762715499275.vrm`** — the avatar (VRM 0.x, full humanoid skeleton incl. all finger
  joints). Served alongside `help.html`.

Because the VRM has real finger bones, the fist is a genuine finger curl (probed flexion axis =
local **Z**), so there is **no clipping** — unlike a rigid mesh. The arm pose is FK on the
VRM humanoid normalized bones; finger curl + the belly→chest lift are keyframed in JS.

### Run it
GLTF/VRM must be served over http (not `file://`):
```
cd D:\ASL_Game\avatar_preview
python -m http.server 8778
```
Open http://127.0.0.1:8778/help.html

### Tune the sign
All in `help.html`:
- `POSE_REST` / `POSE_TOGETHER` / `POSE_LIFT` — arm euler angles (VRM normalized bones).
- `setFist()` — finger curl angles (per joint).
- `T = {...}` — animation timeline (reach / lift / hold seconds).

## Deprecated — robot.blend approach
`build_help_glb.py` + `robot_help.glb` rigged the unrigged `D:\robot.blend` mech (rigid
bone-per-part + a baked finger-curl). Superseded because the robot has no finger bones, so a
clean fist wasn't possible. Kept for reference only.

## Honest caveats
- This pose is **uncalibrated**. Per the paper's Phase 6, a fluent/Deaf signer should review the
  pose targets before it's used as a real teaching reference.
- For a single sign, a recorded human clip is still the most accurate option; this pipeline
  earns its keep when synthesizing a large vocabulary (paper Phase 9).
