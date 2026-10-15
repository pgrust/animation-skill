---
name: animation-skill
description: Build deterministic technical animations in either React and SVG or headless Blender, then render and verify the result. Use SVG for label-heavy diagrams, state transitions, architecture, and fair comparisons. Use Blender when depth, materials, lighting, or physical camera-relative motion explains the mechanism.
---

# Build a verified technical animation

Choose one renderer before you write scene code. Both modes follow the same
truth, state, render, and review contract in
[the shared workflow](references/workflow.md).

## Pick the mode

Use `svg` when the story depends on exact labels, discrete state, flat data
flow, or side-by-side geometry. The mode uses React, TypeScript, SVG, Chrome,
and FFmpeg. Read [the SVG visual direction](modes/svg/references/visual-direction.md)
and [architecture](modes/svg/references/architecture.md) before you add a scene.

Use `blender` when depth, physical transfer, occlusion, materials, lighting,
or camera motion makes the explanation clearer. The mode uses Blender 5.2,
`bpy`, external Python, and FFmpeg. Read
[the Blender visual direction](modes/blender/references/visual-direction.md)
and [project interface](modes/blender/references/project-interface.md) before
you add a project.

If both modes could tell the story, start with `svg`. Do not pay the render and
legibility cost of 3D unless 3D carries information.

## Define the claim

Write one sentence before editing geometry:

> Viewer sees **mechanism** cause **state change**, proving **takeaway**.

Record object identities, events, owners, final state, and illustrative
choices. Verify technical claims against primary material. Do not let visual
timing, distances, or counts imply benchmark data.

## Run SVG mode

Work under `modes/svg/`. Keep events, profiles, validation, and
`getState(timeMs, profile)` in the model. The React component only renders the
returned state.

Use `./animation svg new <scene-name>` to create a pure timeline model, stateless
SVG component, checkpoint contract, and registration instructions. Replace its
placeholder claim and geometry before styling it.

```bash
./animation svg install
./animation svg check
./animation svg capture:checkpoints --scene task-pipeline --profile fast
./animation svg render:video --scene task-pipeline --profile fast --output output/task-pipeline-fast.mp4
```

Before the final render, start `./animation svg dev` and open the scene with
`autoplay=0&feedback=1`. Seek to the relevant frame, click the element being
reviewed, and save one concrete note per problem. Read
`modes/svg/feedback/feedback.jsonl`, address every open note or record why it
does not require a change, then rerun `./animation svg check`. Feedback is
local review evidence: the file is ignored by Git and the overlay never enters
exported frames.

Read the [SVG failure modes](modes/svg/references/failure-modes.md) when browser
state, exported frames, or video disagree. Read the
[SVG portability notes](modes/svg/references/portability.md) before changing
the viewport, browser, codec, typography, or platform.

## Run Blender mode

Work under `modes/blender/`. Keep the event table, scene construction,
assertions, and manifest facts in each project's `build.py`.

Do not turn a flat three-box diagram into a slower 3D diagram. Start from a
scene archetype, use a three-quarter camera, create foreground/midground/depth,
and show enough repeated work to explain concurrency or transformation. Unless
one large transformation is the subject, target 6 to 12 semantic work items
with 2 to 4 visibly in flight at the peak. Use the four beats: orient,
demonstrate one complete operation, accelerate, and land on a held final state.

Treat semantic labels as scene geometry. Stage names, node names, ports, slots,
and work-item IDs must be children of the objects they describe. Surface-align
them by default; use an object-anchored billboard only when no readable surface
faces the camera. They must be lit, depth-tested, occluded by nearer geometry,
and move with their owner. Reserve unanchored camera-facing text for one global
title and, if necessary, one caption or final takeaway. Never put semantic
labels in a camera-space HUD or compositor overlay.

```bash
./animation blender check
./animation blender preview 1 98 220 330
./animation blender timeline
./animation blender final
./animation blender contact-sheet
```

Use `./animation blender new <name>` to create a project. Use
`./animation blender run projects/<name> <command>` to run it. Read the
[Blender failure modes](modes/blender/references/failure-modes.md) when camera,
materials, headless execution, or Blender version behavior fails. Read the
[Blender portability notes](modes/blender/references/portability.md) before
changing the renderer, camera, lighting, codec, or supported Blender version.

Reject the result before the master render if the camera does not expose top,
front, and side faces; the peak frame has no meaningful overlap; arrivals do
not produce a visible destination response; or the same story would be clearer
as three flat cards and one moving dot. Also reject it when a semantic label
floats over the picture instead of visibly belonging to an object.

## Accept the result

Inspect exact semantic checkpoints and the complete encoded video. Check dense
frame strips around short ownership changes. Require source assertions and
media checks to pass. Neither pixels nor structured state can replace the
other.

Do not commit generated frames, videos, or `.blend` files.
