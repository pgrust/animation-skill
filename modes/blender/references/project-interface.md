# Project interface reference

## Supported environment

| Item | Supported value |
| --- | --- |
| Blender | 5.2.x |
| Render engine | `BLENDER_EEVEE` |
| External Python | 3.11 or newer |
| Video tools | `ffmpeg` and `ffprobe` |
| Final video codec | H.264 through `libx264` |
| Final pixel format | `yuv420p` |

The runtime starts Blender with `--background`, `--factory-startup`, and
`--python-exit-code 1`. The scene builder runs in Blender's embedded Python.
The render command runs in external Python and does not import `bpy`.

Read [the visual-direction guide](visual-direction.md) before creating a
project. The interface makes a scene reproducible; that guide supplies the
camera, density, lighting, motion, pacing, and composition defaults that make
the first render useful.

## Project files

Each project directory contains these tracked files:

```text
project-name/
├── project.json
├── build.py
├── render.sh
├── README.md
└── EVAL.md
```

`render.sh` passes its arguments to `scripts/render_project.py`. The shared
runner, not the project shell file, owns cleanup, Blender invocation, frame
checks, encoding, probing, and decoding.

## `project.json`

The configuration uses schema version 1:

```json
{
  "schema_version": 1,
  "name": "parcel-sorter",
  "blender_version": [5, 2],
  "timeline": {
    "frame_start": 1,
    "frame_end": 150,
    "fps": 30
  },
  "render": {
    "engine": "BLENDER_EEVEE",
    "view_transform": "AgX",
    "look": "AgX - Medium High Contrast",
    "transparent_background": false,
    "preview": {
      "width": 640,
      "height": 360,
      "samples": 12
    },
    "final": {
      "width": 1280,
      "height": 720,
      "samples": 32
    }
  },
  "video": {
    "crf": 18,
    "preset": "medium",
    "pixel_format": "yuv420p"
  }
}
```

The frame count is inclusive:

```text
frame_count = frame_end - frame_start + 1
duration_seconds = frame_count / fps
```

Both render dimensions must be positive even numbers because `yuv420p` cannot
represent odd dimensions. The loader rejects unsupported engines and pixel
formats instead of passing them to Blender or FFmpeg.

## `build.py`

The scene builder calls one shared interface:

```python
run_scene(
    build_scene,
    validate_scene=validate_scene,
    manifest_facts=manifest_facts,
)
```

`build_scene(context)` creates all collections, objects, materials, animation,
lights, and the active camera. It returns any state needed by the other two
callbacks.

`validate_scene(context, state)` raises an exception when a semantic or scene
invariant fails. The common runtime already checks the Blender version, active
camera, frame range, and FPS.

`manifest_facts(context, state)` returns JSON-compatible story facts. The
runtime adds render policy, Blender version, frame count, duration, quality,
and object count.

`blender_animation.scene` includes neutral starting tools in addition to basic
geometry: `DEFAULT_PALETTE`, `add_three_quarter_camera`,
`add_three_point_lighting`, `add_attached_label`, `key_camera_pose`, and
`follow_orthographic_camera`. The generated project uses surface-attached stage
and work-item labels. `follow_orthographic_camera` is only for a billboard that
remains parented to a scene object; it is not a semantic HUD helper.

## Render commands

| Command | Result |
| --- | --- |
| `render.sh check` | Validates commands, Blender version, JSON, and Python syntax |
| `render.sh preview [FRAME ...]` | Renders requested checkpoint PNGs in one Blender process |
| `render.sh timeline` | Renders every frame with preview settings and verifies a review MP4 |
| `render.sh final` | Renders every frame with final settings and verifies the master MP4 |
| `render.sh verify` | Rechecks the existing master, manifest, and complete decode |
| `render.sh contact-sheet` | Samples the master by duration and writes one tiled PNG |

Without explicit frames, `preview` renders the first, middle, and last frame.

## Generated output

All generated files stay under `output/`:

```text
output/
├── previews/
├── preview-frames/
├── frames/
├── scene-manifest.json
├── <name>.blend
├── <name>-preview.mp4
├── <name>.mp4
└── contact-sheet.png
```

Git ignores every project `output/` directory.

## Failure behavior

The runner exits nonzero when a required command is missing, the Blender
version differs, the configuration is invalid, the scene callback raises, a
frame filename is missing or extra, media metadata differs, the manifest does
not match, or FFmpeg cannot decode the complete video.

Frame cleanup deletes only files that match `frame_*.png` in the project's
resolved `output/frames/` or `output/preview-frames/` directory. The runner
refuses cleanup outside the project's output directory.
