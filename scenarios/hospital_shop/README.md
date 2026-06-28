# Hospital Scenario

A gamified **hospital communication** scenario for the ASL_Game app. The learner works through a
queue of "patients", each needing one emergency/medical sign, and performs it in front of the
webcam to treat them. It reuses the shared recognition engine (`core/`) and shared game mechanics
(`core/game.py`, `core/overlay.py`) unchanged — only the theme, prompts, and the sign set differ
from the coffee-shop scenario. See the [root README](../../README.md) and
[CLAUDE.md](../../CLAUDE.md) for the overall architecture and the non-negotiable rule.

## Run it

> Activate the venv and download the MediaPipe models first (see [models/README.md](../../models/README.md)).

```bash
python -m scenarios.hospital_shop.main            # play
python -m scenarios.hospital_shop.main --debug    # + live per-parameter score bars
```

Keys: **`q`** quit · **`n`** skip to the next patient (handy for practising one sign).

You can also exercise a single sign on the shared scorecard:

```bash
python -m tools.demo_verify --sign HELP           # or PAIN / MEDICINE / EMERGENCY / LETTER_A
```

## The signs (v1 vocabulary)

Each sign is **data** in `signs/<name>.py`; the generic verifier reads it — there is no per-sign
code path. Movement is **required** on every sign except the two static poses (A, SICK), so a
frozen pose can't pass them.

| Sign | How to perform it | Movement kind | Gated parameters |
|------|-------------------|---------------|------------------|
| **HELP** | A closed **fist** on your open flat **palm**; lift the fist straight **up**. | `linear` (up) | handshape ×2, location, movement |
| **PAIN** | Both hands **index** points, fingertips toward each other; bring them **together**. | `converge` | handshape ×2, movement |
| **MEDICINE** | Open **palm** up; the other a **claw**, twisting **repeatedly** over the palm. | `repeated` | handshape ×2, location, movement |
| **EMERGENCY** | One **claw** raised, **shaken** quickly side to side. | `repeated` | handshape, movement |
| **DOCTOR** | Flat hand: **tap** your fingertips on the opposite **wrist**, twice. | `repeated` (taps) | handshape, location, movement |
| **NURSE** | Two-finger **"N"**: tap on the opposite **wrist**, twice. | `repeated` (taps) | handshape, location, movement |
| **SICK** | **Middle** fingers out — one at your **forehead**, one at your stomach. | `none` (static pose) | handshape ×2, location |
| **FEVER** | Open hand: **sweep** the back of it across your **forehead**. | `linear` (sweep) | handshape, location, movement |
| **WATER** | Three-finger **"W"**: tap on your **chin**, twice. | `repeated` (taps) | handshape, location, movement |
| **BREATHE** | Both **open** hands on your **chest**: move them **out**, then in. | `repeated` (out/in) | handshape ×2, location, movement |
| **HOSPITAL** | Two-finger **"H"** by your opposite **shoulder**: draw a small cross. | `linear` (stroke) | handshape, location, movement |
| **DIZZY** | **Clawed** hand up by your **face**: **circle** it in a small loop. | `circular` | handshape, location, movement |
| **A** (control) | A closed fist, thumb alongside, held **still**. | `none` | handshape only |

The two static signs (`A` in `signs/letter_a.py`, `SICK`) are *allowed* to pass while frozen —
they prove the other half of the contract, that the **movement** signs must fail when frozen.
DOCTOR/NURSE leave the non-dominant "wrist/arm" hand present but **ungated** (its handshape is
whatever); only the tapping hand, the location, and the taps are checked.

> **HELP is a lift.** Because HELP *is* upward motion, settle your hands first, then lift — raising
> your hands into frame is itself motion, so start from rest and make the lift deliberate.

### v1 rule-based limitations (honest caveats)

These are the spots where hand-written geometry is fragile — flagged here, and the reason the
project plans to move to a learned classifier (see the [root README](../../README.md) roadmap):

- **DOCTOR vs NURSE** are a **handshape minimal pair** (flat hand vs two-finger "N"), same wrist
  location and taps. They're separated only by finger count, which is the least-robust thing to
  detect. **HOSPITAL** also uses the two-finger hand and is separated from NURSE only by location
  (shoulder vs wrist) and stroke-vs-taps.
- **SICK**'s wrist *twist* and **DIZZY**'s facial expression aren't recoverable from hand+pose
  landmarks, so they're **described but not gated** — SICK is gated on its distinctive two-location
  middle-finger pose, DIZZY on the circle near the face.
- **MEDICINE ⊃ EMERGENCY**: a claw shaken over a palm contains the one-hand EMERGENCY shake, so a
  full MEDICINE performance also satisfies EMERGENCY. In play this is harmless (the verifier only
  checks the *prompted* sign), and it's locked as the single allowed exception in the
  cross-trigger test.

## How recognition is kept honest

The whole point of this engine is that a sign passes **only** when every required parameter
individually clears its threshold — never an average, never a single frame. Three layers stop a
sign from passing when you are *present but not performing it*:

1. **Movement gates** (`core/movement.py`) — the hospital signs use `linear` / `converge` /
   `repeated` (COFFEE's `circular` is untouched):
   - `repeated` requires real oscillation **amplitude** (≥ 0.05 shoulder-widths) and only counts
     reversals that clear a noise band, so a jittering/near-still claw can't fake "cycles".
   - `linear` has a hard floor — under 0.05 shoulder-widths of travel scores 0 (a drift is not a lift).
   - All distances are ratios of **shoulder width**, so they hold regardless of camera distance.
2. **Required-gating, no averaging** (`core/verifier.py`) — a perfect handshape can never
   compensate for absent required movement.
3. **Flicker-tolerant debounce** (`main.py`) — success fires only when the sign verifies as passed
   on **≥ 4 frames within a 0.6 s window**. This blocks single-frame flukes yet survives the brief
   handshape dropouts that happen mid-motion. An idle hand never clears the movement gate, so it
   accumulates zero passing frames.

## Hospital-specific engine additions

Kept in the **shared** engine (so they're reusable and tested), but only affect the hospital signs:

- **`CONVERGE` movement kind** (`core/schema.py`, `core/movement.py`) — a two-hand "gap closing"
  detector with a `min_approach_ratio` threshold, used by PAIN.
- **Handshapes** (`core/handshape.py`) beyond COFFEE's `fist`: `index`, `open`, `claw`, plus the
  finger-count shapes `n`/`h` (2 fingers — NURSE/HOSPITAL), `w` (3 fingers — WATER) and `middle`
  (SICK). `claw` penalises a wide spread of finger curls so a 2-finger "N" can't read as a claw.
- **Body-location anchors** (`core/schema.py` `Anchor`, scored in `core/verifier.py`): `CHIN`
  and `CHEST` (Saad's, for THANK_YOU/PLEASE), plus `FOREHEAD` (FEVER/SICK/DIZZY — at/above the
  mouth landmark), `BELLY` (low on the torso) and `SHOULDER` (near a shoulder — HOSPITAL). All are
  vertical bands measured in shoulder-widths against the real mouth / shoulder landmarks.
- **`_best_fit_roles`** (`core/verifier.py`) — when a two-handed sign has *different* handshapes
  (HELP = fist+open, MEDICINE = claw+open), the dominant/non-dominant roles are assigned by best
  **fit** to the declared shapes instead of by which hand moved more. Without this, the role labels
  flicker when both hands move together and the handshape scores swap 1.0↔0.0. Symmetric signs
  (COFFEE = fist+fist) and one-handed signs are left exactly as the motion heuristic returned them.

## Testing & fixtures

```bash
pytest tests/test_hospital.py -v
```

Every **movement** sign ships **three** fixtures, all replayed through the same verifier:

| Fixture | Represents | Asserted result |
|---------|-----------|-----------------|
| `<sign>_correct`  | the sign performed properly | **PASS** (movement clears) |
| `<sign>_confusor` | frozen in the correct pose | **FAIL on `movement`** |
| `<sign>_idle`     | correct handshape held with incidental jitter, **no sign motion** | **FAIL on `movement`** |

The `_idle` fixtures are the regression lock for the cardinal *"passing without performing"* bug.
The static **SICK** pose can't be gated on movement, so instead it ships `sick_wrongshape` (open
hands → fail on handshape) and `sick_lowhand` (hand not at the forehead → fail on location). A
**`test_no_cross_trigger`** test also asserts each sign's correct performance is accepted as *only*
its own sign (the one allowed exception being MEDICINE ⊃ EMERGENCY).

**Fixtures are deterministic synthetic clips** (geometrically constructed, flagged
`"synthetic": true`) so the suite is reproducible in CI without a webcam. Regenerate them with:

```bash
python -m tools.make_synth_fixtures
```

To replace any fixture with a **real** webcam recording (preferred for building our own dataset),
record over the same filename — the test picks it up automatically:

```bash
python -m tools.record_fixture --name help_correct --seconds 4 --sign HELP
```

## Adding a hospital sign

Follow the safe workflow in the [root README](../../README.md#adding-a-new-sign-safe-workflow):
define it in `signs/<name>.py`, add it to `signs/__init__.py` and the `PATIENTS` queue in
`main.py`, ship a `correct` + `confusor` (+ ideally `idle`) fixture, add a test, and run the
pre-ship checklist. If the sign needs a new movement type or handshape, add it to the shared
engine (with the amplitude/floor guards above) — never inside this scenario folder.

## Known limitations (v1, rule-based)

- **HELP** is the hardest sign: it conjoins four conditions during a transient lift, so it needs a
  deliberate motion and good lighting. The handshape flicker on a moving fist is a real-data limit
  that the planned learned classifier (see the root README roadmap) will resolve.
- **MEDICINE** has the two hands overlapping, so MediaPipe occasionally drops one — keep a little
  separation between the claw and the palm.
- Recognition needs both hands fully in frame with reasonable lighting; a missing landmark can't be
  recovered by rules.
