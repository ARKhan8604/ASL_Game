"""Headless Blender: rig robot.blend's arms with a rigid empty-joint hierarchy,
animate the ASL HELP sign (dominant fist rests on open non-dominant palm, both lift up),
decimate for the web, and export a GLB the Three.js page plays via AnimationMixer.

Run:  blender --background --python build_help_glb.py
"""
import bpy, math
from mathutils import Vector, Quaternion

SRC = r"D:\robot.blend"
OUT = r"D:\ASL_Game\avatar_preview\robot_help.glb"
DECIMATE = 0.18          # collapse ratio for web payload (stylized look is fine)
ANIMATE  = True          # False = export a single static pose for pivot validation
D = math.radians

# ---- joint pivot positions in Blender world space (Z up), estimated from bboxes ----
JOINTS = {
    "R_Shoulder": Vector(( 20.0,  9.0, 150.0)),
    "R_Elbow":    Vector(( 29.0, 12.0, 120.0)),
    "R_Wrist":    Vector(( 33.0,  4.0,  98.0)),
    "L_Shoulder": Vector((-20.0,  9.0, 150.0)),
    "L_Elbow":    Vector((-29.0, 12.0, 120.0)),
    "L_Wrist":    Vector((-33.0,  4.0,  98.0)),
}

# ---- HELP key poses defined by WRIST TARGETS (Blender coords: +X right, -Y front, +Z up).
# Solved into shoulder/elbow rotations by the analytical 2-bone IK below (paper Phase 4).
# Dominant = RIGHT (fist, rests on top); non-dominant = LEFT (open palm platform, lower).
TARGETS_TOGETHER = {   # hands meet front-center at belly height; right fist sits on left palm
    "R": Vector(( 2.0, -30.0, 116.0)),
    "L": Vector((-2.0, -30.0, 108.0)),
}
TARGETS_LIFTED = {     # both lift straight up to mid-chest (the HELP "lifting someone up")
    "R": Vector(( 2.0, -28.0, 138.0)),
    "L": Vector((-2.0, -28.0, 130.0)),
}
# pole vector per side: where the elbow should point (outward, slightly back & down)
POLE = {"R": Vector(( 2.0, 1.0, -1.5)), "L": Vector((-2.0, 1.0, -1.5))}

bpy.ops.wm.open_mainfile(filepath=SRC)
scene = bpy.context.scene

# ---- make a fist on the DOMINANT (right) hand by baking a curl into the finger
# geometry (everything below the knuckle line). The robot has no finger bones, so we
# rotate the sub-knuckle vertices about the knuckle pivot directly in mesh data. -----
from mathutils import Matrix
MAKE_FIST   = True
FIST_KNUCKLE_Z = 89.0          # world Z of the knuckle line; verts below this = fingers
FIST_PIVOT  = Vector((34.0, 1.0, 89.0))   # right-hand knuckle pivot (world)
FIST_ANGLE  = math.radians(125)
FIST_AXIS   = 'X'

def mesh_center_x_data(ob):
    cs = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    return sum(c.x for c in cs) / 8.0

def make_fist():
    rot = Matrix.Rotation(FIST_ANGLE, 4, FIST_AXIS)
    moved = 0
    for ob in bpy.data.objects:
        if ob.type != 'MESH' or "Hand" not in ob.name:
            continue
        if mesh_center_x_data(ob) < 0:      # right hand only (dominant)
            continue
        mw = ob.matrix_world.copy()
        mwi = mw.inverted()
        for v in ob.data.vertices:
            w = mw @ v.co
            if w.z < FIST_KNUCKLE_Z:
                w = FIST_PIVOT + rot @ (w - FIST_PIVOT)
                v.co = mwi @ w
                moved += 1
        ob.data.update()
    print("FIST_VERTS_MOVED", moved)

if MAKE_FIST:
    make_fist()

# ---- create empties at joints ----
empties = {}
for name, pos in JOINTS.items():
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = 6
    e.location = pos
    scene.collection.objects.link(e)
    empties[name] = e

root = bpy.data.objects.new("Root", None)
root.location = Vector((0, 0, 0))
scene.collection.objects.link(root)
empties["Root"] = root

bpy.context.view_layer.update()

def parent_clean(child, parent):
    """Parent while preserving world transform AND keeping matrix_parent_inverse
    identity, so the hierarchy exports to glTF (parent->child TRS only) correctly."""
    cw = child.matrix_world.copy()
    child.parent = parent
    child.matrix_parent_inverse.identity()
    child.matrix_world = cw
    bpy.context.view_layer.update()

# nest joints (parents before children, updating between so matrix_world is current)
parent_clean(empties["R_Shoulder"], root)
parent_clean(empties["L_Shoulder"], root)
parent_clean(empties["R_Elbow"], empties["R_Shoulder"])
parent_clean(empties["L_Elbow"], empties["L_Shoulder"])
parent_clean(empties["R_Wrist"], empties["R_Elbow"])
parent_clean(empties["L_Wrist"], empties["L_Elbow"])

# ---- parent each mesh to the correct joint (rigid), everything else to Root ----
def mesh_center_x(ob):
    cs = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    return sum(c.x for c in cs) / 8.0

counts = {"R_Shoulder":0,"R_Elbow":0,"R_Wrist":0,"L_Shoulder":0,"L_Elbow":0,"L_Wrist":0,"Root":0}
for ob in list(bpy.data.objects):
    if ob.type != 'MESH':
        continue
    n = ob.name
    cx = mesh_center_x(ob)
    target = "Root"
    if "Arm_Upper" in n:
        target = "R_Shoulder" if cx > 0 else "L_Shoulder"
    elif "Arm_Lower" in n:
        target = "R_Elbow" if cx > 0 else "L_Elbow"
    elif "Hand" in n:
        target = "R_Wrist" if cx > 0 else "L_Wrist"
    parent_clean(ob, empties[target])
    counts[target] += 1
    # decimate
    if DECIMATE < 1.0 and len(ob.data.vertices) > 200:
        m = ob.modifiers.new("dec", 'DECIMATE')
        m.ratio = DECIMATE

print("PARENT_COUNTS", counts)

# --------------------------------------------------------------------------- IK
def clamp(v, lo, hi):
    return max(lo, min(hi, v))

def solve_arm(side, target):
    """Analytical 2-bone IK (Law of Cosines + pole vector), per paper Phase 4.
    Returns (shoulder_euler, elbow_euler) in the empties' local spaces.
    Rest joint positions are the JOINTS dict (chain is at rest when we solve)."""
    S = JOINTS[f"{side}_Shoulder"]
    E = JOINTS[f"{side}_Elbow"]
    W = JOINTS[f"{side}_Wrist"]
    L1 = (E - S).length
    L2 = (W - E).length
    rest_ua = (E - S).normalized()
    rest_fa = (W - E).normalized()

    to_t = target - S
    dist = clamp(to_t.length, 1e-4, (L1 + L2) * 0.999)
    dir = to_t.normalized()

    # shoulder interior angle between (T-S) and the upper arm, via Law of Cosines
    cos_s = clamp((L1 * L1 + dist * dist - L2 * L2) / (2 * L1 * dist), -1.0, 1.0)
    a_shoulder = math.acos(cos_s)

    # bend plane: rotate `dir` toward the pole by a_shoulder to get the upper-arm direction
    pole = POLE[side]
    axis = dir.cross(pole)
    if axis.length < 1e-5:
        axis = dir.cross(Vector((0, 0, 1)))
    axis.normalize()
    ua_dir = (Quaternion(axis, a_shoulder) @ dir).normalized()
    E_new = S + ua_dir * L1
    fa_dir = (target - E_new).normalized()

    # world rotations from rest directions, then express elbow in shoulder-local space
    Qs = rest_ua.rotation_difference(ua_dir)          # shoulder parent = root (world)
    Qfe = rest_fa.rotation_difference(fa_dir)          # desired forearm world rotation
    Qe_local = Qs.inverted() @ Qfe
    return Qs.to_euler(), Qe_local.to_euler()

def apply_targets(targets):
    for side in ("R", "L"):
        sh, el = solve_arm(side, targets[side])
        empties[f"{side}_Shoulder"].rotation_euler = sh
        empties[f"{side}_Elbow"].rotation_euler = el
        empties[f"{side}_Wrist"].rotation_euler = (0, 0, 0)

def apply_rest():
    for k in JOINTS:
        empties[k].rotation_euler = (0, 0, 0)

def key_current(frame):
    for k in JOINTS:
        empties[k].keyframe_insert("rotation_euler", frame=frame)

if ANIMATE:
    scene.frame_start = 1
    scene.frame_end = 80
    apply_rest();                      key_current(1)
    apply_targets(TARGETS_TOGETHER);   key_current(22); key_current(30)   # reach + settle
    apply_targets(TARGETS_LIFTED);     key_current(55); key_current(72)   # lift + hold
    scene.frame_set(1)
else:
    apply_targets(TARGETS_TOGETHER)

bpy.context.view_layer.update()

bpy.ops.export_scene.gltf(
    filepath=OUT,
    export_format='GLB',
    use_selection=False,
    export_apply=True,            # bake modifiers (decimate)
    export_yup=True,              # Blender Z-up -> glTF/three.js Y-up
    export_animations=ANIMATE,
    export_animation_mode='ACTIONS',
)
print("EXPORTED", OUT)
