# MediaPipe model files

The recognition engine uses the MediaPipe **Tasks API**, which loads `.task` model bundles.
These files are **not committed** (they're binary weights, git-ignored via `*.task`). Each
developer downloads them once into this folder.

## Required files

| File                        | Purpose                  | Download |
|-----------------------------|--------------------------|----------|
| `hand_landmarker.task`      | 21 landmarks per hand    | https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker#models |
| `pose_landmarker_lite.task` | body pose (shoulders for normalization) | https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker#models |

The `_lite` pose model is enough — we only need the shoulder points for scale normalization.

## Download commands (run from the repo root)

**Git Bash / macOS / Linux:**
```bash
curl -sSL -o models/hand_landmarker.task \
  "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
curl -sSL -o models/pose_landmarker_lite.task \
  "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task"
```

**Windows PowerShell:**
```powershell
Invoke-WebRequest "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task" -OutFile models/hand_landmarker.task
Invoke-WebRequest "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task" -OutFile models/pose_landmarker_lite.task
```

After downloading, this folder should contain (the `.task` files are git-ignored):

```
models/
├── README.md                 (committed)
├── hand_landmarker.task      (~7.8 MB, git-ignored)
└── pose_landmarker_lite.task (~5.8 MB, git-ignored)
```
