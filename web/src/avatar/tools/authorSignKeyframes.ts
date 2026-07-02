#!/usr/bin/env node
/**
 * Reference Pose System — CODE-AUTHORED keyframes (the "Claude authors a sign" experiment).
 *
 * Third way to produce reference poses, alongside extractReferencePose.ts (static Blender pose) and
 * extractBakedAnimation.ts (baked Blender clip): keyframes are authored HERE as anatomical intent
 * (wrist targets measured off the rig's own chin/chest positions, palm roll, wrist flexion), solved
 * into bone rotations by the SAME validated 2-bone IK the procedural path uses, then FK-VERIFIED
 * (wrist really lands on target, palm normal really points where intended) before anything is
 * written. Output is ordinary ReferencePoseMetadata, so KeyframeAnimator/AnimationSource consume it
 * with zero changes — and a later human-authored Blender clip for the same sign simply REPLACES
 * these files (delete + re-extract), no code involved.
 *
 * Every keyframe below is a hypothesis about how the sign looks; the human eye in AvatarLab is the
 * final judge. FK numbers printed by --verify only guarantee the pose is self-consistent and
 * anatomically plausible, not that it reads as natural ASL.
 *
 * Usage:
 *   npx tsx src/avatar/tools/authorSignKeyframes.ts THANK_YOU            (verify only, prints FK report)
 *   npx tsx src/avatar/tools/authorSignKeyframes.ts THANK_YOU --write    (verify, then write metadata)
 */
import { mkdirSync, readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { parseGlb } from '../calibration/glbBinary.ts';
import { buildHierarchy } from '../calibration/SkeletonInspector.ts';
import { buildCalibration } from '../calibration/CalibrationEngine.ts';
import type { AvatarHierarchy, HandSide, Quat, Vec3 } from '../calibration/types.ts';
import {
  cross, distance, dot, fromTRS, getTranslation, multiply, normalize, quatIdentity,
  quatInvert, quatMultiply, rotateVec3, subtract,
} from '../calibration/math3d.ts';
import type { Mat4 } from '../calibration/math3d.ts';
import { computeBodyFrame, targetWorld } from '../animation/BodyFrame.ts';
import { poseArm } from '../animation/ArmRetargeter.ts';
import { SIGN_PATHS } from '../animation/signPaths.ts';
import type { ReferencePoseIndex, ReferencePoseMetadata } from '../reference/types.ts';

// ---------------------------------------------------------------------------------------------
// Authored sign specs. Offsets are body-frame, in shoulder-width units, anchored to a named bone
// (same convention as signPaths.ts), so they scale to any avatar. Angles are degrees.
// Sign conventions were established EMPIRICALLY from this tool's FK readout, not assumed:
//   forearmRollDeg: negative = supination for the RIGHT arm (palm normal swings toward frame.up).
//                   The LEFT arm mirrors — tune per-keyframe against the printed palm normal.
//   wristFlexDeg:   negative tilts fingertips up (about the body-frame right axis).
// ---------------------------------------------------------------------------------------------

interface ArmKeyframeSpec {
  /** Wrist target = anchor bone's rest world position + body-frame offset * shoulderWidth. */
  anchor: string;
  offset: Vec3;
  forearmRollDeg: number;
  wristFlexDeg: number;
  /** 'fist' curls every finger joint (S-handshape); omitted/'flat' leaves fingers at rest. */
  handshape?: 'fist' | 'flat';
}

interface AuthoredKeyframe {
  frameFraction: number;
  arms: Partial<Record<HandSide, ArmKeyframeSpec>>;
  notes: string;
}

interface AuthoredSign {
  signName: string;
  poseIdPrefix: string;
  keyframes: AuthoredKeyframe[];
}

/** COFFEE's circling dominant fist: wrist target on a horizontal circle above the resting fist. */
function coffeeCircleKf(fraction: number, angleDeg: number): AuthoredKeyframe {
  const a = (angleDeg * Math.PI) / 180;
  const r = 0.11; // circle radius in shoulder-width units (~4cm on this rig)
  return {
    frameFraction: fraction,
    arms: {
      right: {
        anchor: 'Spine2',
        // Circle centered directly OVER the left fist (same x/z base), raised ~0.24SW (~9cm).
        offset: { x: -0.06 + r * Math.cos(a), y: -0.38, z: 0.78 + r * Math.sin(a) },
        forearmRollDeg: 35, // grinding fist angled palm-down-left, like gripping a crank knob
        wristFlexDeg: 20, // knuckles angled slightly down over the bottom fist
        handshape: 'fist',
      },
      left: {
        anchor: 'Spine2',
        offset: { x: -0.06, y: -0.62, z: 0.78 },
        forearmRollDeg: 20, // bottom fist rolled so the palm faces the signer's right (thumb up)
        wristFlexDeg: 0,
        handshape: 'fist',
      },
    },
    notes: `Dominant fist circling over the stationary non-dominant fist (${angleDeg}deg around the circle).`,
  };
}

const AUTHORED_SIGNS: Record<string, AuthoredSign> = {
  // THANK_YOU: flat dominant hand, fingertips at the chin, palm toward the face; the hand arcs
  // forward and down toward the listener, finishing in front of the chest, palm up.
  THANK_YOU: {
    signName: 'THANK_YOU',
    poseIdPrefix: 'THANKYOU_auth',
    keyframes: [
      {
        frameFraction: 0.0,
        arms: {
          right: { anchor: 'Head', offset: { x: 0.12, y: -0.45, z: 0.36 }, forearmRollDeg: -70, wristFlexDeg: -15 },
        },
        notes: 'Fingertips at chin, palm toward face.',
      },
      {
        frameFraction: 0.2,
        arms: {
          right: { anchor: 'Head', offset: { x: 0.12, y: -0.45, z: 0.36 }, forearmRollDeg: -70, wristFlexDeg: -15 },
        },
        notes: 'Brief hold at the chin before the outward arc.',
      },
      {
        frameFraction: 0.6,
        arms: {
          right: { anchor: 'Head', offset: { x: 0.16, y: -0.75, z: 0.75 }, forearmRollDeg: -40, wristFlexDeg: 0 },
        },
        notes: 'Mid-arc: hand moving forward and down, palm rotating up.',
      },
      {
        frameFraction: 1.0,
        arms: {
          right: { anchor: 'Head', offset: { x: 0.24, y: -1.0, z: 1.12 }, forearmRollDeg: -110, wristFlexDeg: 0 },
        },
        notes: 'Arm extended toward the listener, palm up — offering the thanks.',
      },
    ],
  },

  // COFFEE: non-dominant S-hand (left fist) stationary at lower-chest height; dominant S-hand
  // (right fist) rests just above it and grinds in a horizontal circle — like cranking a coffee
  // mill. One full circle across the clip (start angle = end angle, so looping playback is smooth).
  COFFEE: {
    signName: 'COFFEE',
    poseIdPrefix: 'COFFEE_auth',
    keyframes: [
      coffeeCircleKf(0.0, 0),
      coffeeCircleKf(0.2, 72),
      coffeeCircleKf(0.4, 144),
      coffeeCircleKf(0.6, 216),
      coffeeCircleKf(0.8, 288),
      coffeeCircleKf(1.0, 360),
    ],
  },

  // YES: dominant S-hand held in front of the shoulder, "nodding" at the wrist (flex down, back up,
  // down again) — the arm itself barely moves; the motion is all wrist flexion.
  YES: {
    signName: 'YES',
    poseIdPrefix: 'YES_auth',
    keyframes: [
      {
        frameFraction: 0.0,
        arms: {
          right: { anchor: 'RightArm', offset: { x: 0.05, y: -0.45, z: 0.85 }, forearmRollDeg: -20, wristFlexDeg: -20, handshape: 'fist' },
        },
        notes: 'Fist up in front of the shoulder, wrist neutral-extended.',
      },
      {
        frameFraction: 0.25,
        arms: {
          right: { anchor: 'RightArm', offset: { x: 0.05, y: -0.48, z: 0.85 }, forearmRollDeg: -20, wristFlexDeg: 40, handshape: 'fist' },
        },
        notes: 'First nod: wrist flexed down.',
      },
      {
        frameFraction: 0.5,
        arms: {
          right: { anchor: 'RightArm', offset: { x: 0.05, y: -0.45, z: 0.85 }, forearmRollDeg: -20, wristFlexDeg: -20, handshape: 'fist' },
        },
        notes: 'Back up between nods.',
      },
      {
        frameFraction: 0.75,
        arms: {
          right: { anchor: 'RightArm', offset: { x: 0.05, y: -0.48, z: 0.85 }, forearmRollDeg: -20, wristFlexDeg: 40, handshape: 'fist' },
        },
        notes: 'Second nod: wrist flexed down.',
      },
      {
        frameFraction: 1.0,
        arms: {
          right: { anchor: 'RightArm', offset: { x: 0.05, y: -0.45, z: 0.85 }, forearmRollDeg: -20, wristFlexDeg: -20, handshape: 'fist' },
        },
        notes: 'Wrist back up — sign complete.',
      },
    ],
  },
};

// ---------------------------------------------------------------------------------------------

function fail(message: string): never {
  console.error(`FAIL: ${message}`);
  process.exit(1);
}

function axisAngleQuat(axis: Vec3, deg: number): Quat {
  const a = normalize(axis);
  const half = (deg * Math.PI) / 360;
  const s = Math.sin(half);
  return { x: a.x * s, y: a.y * s, z: a.z * s, w: Math.cos(half) };
}

function restWorldQuat(hierarchy: AvatarHierarchy, boneName: string | null): Quat {
  if (!boneName) return quatIdentity();
  const bone = hierarchy.bones[boneName];
  return quatMultiply(restWorldQuat(hierarchy, bone.parent), bone.localRotation);
}

function worldMatrixWithOverrides(
  hierarchy: AvatarHierarchy,
  boneName: string,
  overrides: Record<string, Quat>,
  cache: Map<string, Mat4>
): Mat4 {
  const cached = cache.get(boneName);
  if (cached) return cached;
  const bone = hierarchy.bones[boneName];
  const local = fromTRS(bone.localPosition, overrides[boneName] ?? bone.localRotation, bone.localScale);
  const world = bone.parent ? multiply(worldMatrixWithOverrides(hierarchy, bone.parent, overrides, cache), local) : local;
  cache.set(boneName, world);
  return world;
}

const [signArg, writeFlag] = process.argv.slice(2);
if (!signArg) fail(`Usage: authorSignKeyframes.ts <signName> [--write]\nAuthored signs: ${Object.keys(AUTHORED_SIGNS).join(', ')}`);
const spec = AUTHORED_SIGNS[signArg];
if (!spec) fail(`No authored keyframes for "${signArg}". Available: ${Object.keys(AUTHORED_SIGNS).join(', ')}`);
if (!(spec.signName in SIGN_PATHS)) {
  // Not fatal: keyframe-driven signs don't need a procedural path — AnimationSource's keyframe
  // resolver works for any sign with >=2 poses. The sign just won't have an IK fallback.
  console.log(`note: "${spec.signName}" has no SIGN_PATHS entry — keyframes will be its ONLY animation source.\n`);
}
const doWrite = writeFlag === '--write';

const REPO_ROOT = resolve(import.meta.dirname, '../../../..');
const SOURCE_DIR = resolve(REPO_ROOT, 'reference_poses');
const PUBLIC_DIR = resolve(import.meta.dirname, '../../../public/reference_poses');
const REST_RIG_PATH = resolve(import.meta.dirname, '../../../public/models/avatar/ybot.glb');

const raw = readFileSync(REST_RIG_PATH);
const buffer = raw.buffer.slice(raw.byteOffset, raw.byteOffset + raw.byteLength);
const hierarchy = buildHierarchy(parseGlb(buffer).json, REST_RIG_PATH);
const calibration = buildCalibration(hierarchy, buffer);
const frame = computeBodyFrame(hierarchy);

console.log(`Authoring "${spec.signName}" (${spec.keyframes.length} keyframes) on ${hierarchy.sourceFile}`);
console.log(`Body frame: right=(${frame.right.x.toFixed(2)},${frame.right.y.toFixed(2)},${frame.right.z.toFixed(2)}) shoulderWidth=${frame.shoulderWidth.toFixed(3)}m\n`);

interface BuiltKeyframe {
  kf: AuthoredKeyframe;
  bones: ReferencePoseMetadata['bones'];
}

/** Solves one arm's spec into local bone rotations; returns them plus an FK sanity report line. */
function buildArm(side: HandSide, armSpec: ArmKeyframeSpec): { bones: Record<string, Quat>; report: string; sane: boolean } {
  const chain = hierarchy.arms[side];
  if (!chain.upperArm || !chain.forearm || !chain.hand) fail(`${side} arm chain incomplete.`);
  const armName = chain.upperArm;
  const foreName = chain.forearm;
  const handName = chain.hand;

  const targetW = targetWorld(hierarchy, frame, armSpec.anchor, armSpec.offset);
  const pose = poseArm(hierarchy, calibration, frame, side, targetW);

  // World quaternions after the IK solve, so roll/flexion can be applied about unambiguous world axes.
  const armParentWorld = restWorldQuat(hierarchy, hierarchy.bones[armName].parent);
  const armWorld = quatMultiply(armParentWorld, pose.upperArmLocalRotation);
  const forearmAxisWorld = normalize(subtract(pose.achievedHandWorld, pose.elbowWorld));

  // Roll the forearm about its own (post-solve) bone axis: hand position is unchanged, palm turns.
  const rollQuat = axisAngleQuat(forearmAxisWorld, -armSpec.forearmRollDeg);
  const foreWorld0 = quatMultiply(armWorld, pose.forearmLocalRotation);
  const foreWorld = quatMultiply(rollQuat, foreWorld0);
  const foreLocal = quatMultiply(quatInvert(armWorld), foreWorld);

  // Tilt the wrist about the body-frame right axis (sagittal-plane flexion — adequate while the
  // hand works in front of the torso, which covers every keyframe authored above).
  const flexQuat = axisAngleQuat(frame.right, -armSpec.wristFlexDeg);
  const handWorld0 = quatMultiply(foreWorld, hierarchy.bones[handName].localRotation);
  const handWorld = quatMultiply(flexQuat, handWorld0);
  const handLocal = quatMultiply(quatInvert(foreWorld), handWorld);

  const bones: Record<string, Quat> = {
    [armName]: pose.upperArmLocalRotation,
    [foreName]: foreLocal,
    [handName]: handLocal,
  };
  if (armSpec.handshape === 'fist') Object.assign(bones, buildFist(side));

  // ---- FK verification: where do the wrist / fingers ACTUALLY end up with these rotations? ----
  const cache = new Map<string, Mat4>();
  const wristFk = getTranslation(worldMatrixWithOverrides(hierarchy, handName, bones, cache));
  const wristErr = distance(wristFk, targetW);

  let fistReport = '';
  if (armSpec.handshape === 'fist') {
    const middleChain = hierarchy.hands[side]?.fingers['middle'];
    if (middleChain && middleChain.length > 0) {
      const tip = getTranslation(worldMatrixWithOverrides(hierarchy, middleChain[middleChain.length - 1], bones, cache));
      fistReport = `  fist: middle tip->wrist=${(distance(tip, wristFk) * 1000).toFixed(0)}mm (flat rest ~130mm, fist optimum ~91mm on this rig)`;
    }
  }

  const fingers = hierarchy.hands[side]?.fingers ?? {};
  const indexMcp = fingers['index']?.[0];
  const pinkyMcp = fingers['pinky']?.[0];
  const middleMcp = fingers['middle']?.[0];
  let palmReport = 'palm: (finger bones not discovered)';
  if (indexMcp && pinkyMcp && middleMcp) {
    const iPos = getTranslation(worldMatrixWithOverrides(hierarchy, indexMcp, bones, cache));
    const pPos = getTranslation(worldMatrixWithOverrides(hierarchy, pinkyMcp, bones, cache));
    const mPos = getTranslation(worldMatrixWithOverrides(hierarchy, middleMcp, bones, cache));
    // Palm normal points out of the palm side: cross order flips between hands (mirrored anatomy).
    const va = subtract(iPos, wristFk);
    const vb = subtract(pPos, wristFk);
    const palmN = normalize(side === 'right' ? cross(va, vb) : cross(vb, va));
    const fingerDir = normalize(subtract(mPos, wristFk));
    palmReport =
      `palm up=${dot(palmN, frame.up).toFixed(2)} fwd=${dot(palmN, frame.forward).toFixed(2)} rt=${dot(palmN, frame.right).toFixed(2)} | ` +
      `fingers up=${dot(fingerDir, frame.up).toFixed(2)} fwd=${dot(fingerDir, frame.forward).toFixed(2)}`;
  }

  const shoulderY = hierarchy.bones[armName].worldPosition.y;
  const sane = wristErr < 0.02 && pose.elbowWorld.y < shoulderY + 0.02;
  const report =
    `${side.padEnd(5)} wrist err=${(wristErr * 1000).toFixed(1)}mm  elbow y=${pose.elbowWorld.y.toFixed(3)} (shoulder ${shoulderY.toFixed(3)})  ${sane ? 'OK' : 'SUSPECT'}\n` +
    `        wrist=(${wristFk.x.toFixed(3)}, ${wristFk.y.toFixed(3)}, ${wristFk.z.toFixed(3)})  ${palmReport}${fistReport}`;
  return { bones, report, sane };
}

/**
 * Local rotations that curl one hand into an S-handshape (fist). The curl axis for each joint is
 * NEVER assumed: for each finger both curl directions are tried and FK decides — the direction that
 * brings the fingertip closest to the wrist wins. Depends only on the rig's REST pose (local-frame
 * geometry is invariant to whatever the arm/wrist are doing), so the result is cached per side.
 */
const fistCache = new Map<HandSide, Record<string, Quat>>();
function buildFist(side: HandSide): Record<string, Quat> {
  const cached = fistCache.get(side);
  if (cached) return cached;

  const hand = hierarchy.hands[side];
  const wristName = hierarchy.arms[side].hand;
  if (!hand || !wristName) fail(`No ${side} hand/finger chains discovered on this rig.`);
  const fingers = hand.fingers;
  const idx = fingers['index']?.[0];
  const pky = fingers['pinky']?.[0];
  if (!idx || !pky) fail(`${side} hand is missing index/pinky chains — cannot derive a curl axis.`);

  // Transverse axis of the palm at rest (index MCP -> pinky MCP): curling is a rotation about this
  // line (or its negation — FK picks below).
  const axisW = normalize(subtract(hierarchy.bones[pky].worldPosition, hierarchy.bones[idx].worldPosition));
  const wristRest = hierarchy.bones[wristName].worldPosition;

  // 70/95/60 measured as near-optimal on this rig: pushing higher (85/105/75) INCREASED middle
  // tip->wrist from 91mm to 101mm — overcurl, fingers spiraling past the palm.
  const CURL_DEG = { finger: [70, 95, 60], thumb: [35, 40, 25] };
  const result: Record<string, Quat> = {};

  for (const [fingerName, chain] of Object.entries(fingers)) {
    if (!chain || chain.length === 0) continue;
    const isThumb = fingerName.toLowerCase().includes('thumb');
    const angles = isThumb ? CURL_DEG.thumb : CURL_DEG.finger;
    const tipBone = chain[chain.length - 1];

    let best: { rotations: Record<string, Quat>; tipToWrist: number } | null = null;
    for (const sign of [1, -1]) {
      const rotations: Record<string, Quat> = {};
      for (let j = 0; j < Math.min(angles.length, chain.length); j++) {
        const boneName = chain[j];
        const bone = hierarchy.bones[boneName];
        // Express the world-space curl axis in this joint's own local frame, then apply the curl as
        // a post-rotation of the rest local rotation (rotation in the bone's own frame).
        const axisL = rotateVec3(axisW, quatInvert(restWorldQuat(hierarchy, boneName)));
        rotations[boneName] = quatMultiply(bone.localRotation, axisAngleQuat(axisL, sign * angles[j]));
      }
      const tip = getTranslation(worldMatrixWithOverrides(hierarchy, tipBone, rotations, new Map()));
      const tipToWrist = distance(tip, wristRest);
      if (!best || tipToWrist < best.tipToWrist) best = { rotations, tipToWrist };
    }
    Object.assign(result, best!.rotations);
  }

  fistCache.set(side, result);
  return result;
}

const built: BuiltKeyframe[] = [];
let allSane = true;

for (const kf of spec.keyframes) {
  const bones: ReferencePoseMetadata['bones'] = {};
  console.log(`kf t=${kf.frameFraction.toFixed(2)}  ${kf.notes}`);
  for (const side of ['right', 'left'] as HandSide[]) {
    const armSpec = kf.arms[side];
    if (!armSpec) continue;
    const armResult = buildArm(side, armSpec);
    allSane &&= armResult.sane;
    console.log(`  ${armResult.report}`);
    for (const [name, rotation] of Object.entries(armResult.bones)) {
      const rest = hierarchy.bones[name];
      bones[name] = {
        rotation: [rotation.x, rotation.y, rotation.z, rotation.w],
        translation: [rest.localPosition.x, rest.localPosition.y, rest.localPosition.z],
      };
    }
  }
  built.push({ kf, bones });
}

if (!allSane) fail('One or more keyframes failed FK sanity (wrist off-target or elbow above shoulder). Nothing written.');

if (!doWrite) {
  console.log('\nVerify-only run — pass --write to persist these keyframes as reference poses.');
  process.exit(0);
}

const writtenIds: string[] = [];
for (let i = 0; i < built.length; i++) {
  const { kf, bones } = built[i];
  const poseId = `${spec.poseIdPrefix}_${String(i).padStart(2, '0')}`;
  const metadata: ReferencePoseMetadata = {
    poseId,
    signName: spec.signName,
    frameFraction: kf.frameFraction,
    sourceGlb: '', // no GLB — authored in code; the spec above is the source of truth
    avatarVersion: calibration.avatarVersion,
    generatorVersion: 'authorSignKeyframes@1.1.0',
    extractedAt: new Date().toISOString(),
    notes: `CODE-AUTHORED (experiment: model-authored keyframes, no Blender source). ${kf.notes}`,
    bones,
  };
  for (const dir of [SOURCE_DIR, PUBLIC_DIR]) {
    mkdirSync(resolve(dir, 'metadata'), { recursive: true });
    writeFileSync(resolve(dir, 'metadata', `${poseId}.json`), JSON.stringify(metadata, null, 2), 'utf-8');
  }
  writtenIds.push(poseId);
}

for (const dir of [SOURCE_DIR, PUBLIC_DIR]) {
  const files = readdirSync(resolve(dir, 'metadata')).filter((f) => f.endsWith('.json') && f !== 'index.json');
  const index: ReferencePoseIndex = { poses: files.map((f) => f.replace(/\.json$/, '')).sort(), updatedAt: new Date().toISOString() };
  writeFileSync(resolve(dir, 'metadata', 'index.json'), JSON.stringify(index, null, 2), 'utf-8');
}

console.log(`\nWrote ${writtenIds.length} poses: ${writtenIds.join(', ')}`);
console.log(`AnimationSource will now prefer keyframe-driven output for "${spec.signName}".`);
