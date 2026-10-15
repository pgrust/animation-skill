# Build an animation from verified state

Use this guide before either renderer's mode-specific references.

## State the visible claim

Write one sentence:

> Viewer sees **mechanism** cause **state change**, proving **takeaway**.

List the semantic objects, stable IDs, event order, owners, final state, and
completion condition. Mark sample values, timing, geometry, and overlap as
illustrative when they do not come from measurements.

## Choose the renderer

Use SVG for exact labels, flat architecture, discrete state, and fair
comparisons. Use Blender when depth, physical assembly, material state,
lighting, or camera-relative occlusion helps the viewer understand the event.

If the choice is close, use SVG. A 3D scene costs more to render and gives text
less screen space.

## Keep one event source

Define each repeated action once. Derive movers, source and destination
visibility, counters, progress, and final assertions from that definition.
One object must never have two visible owners or no owner during a handoff.

Keep technical state separate from presentation. SVG scenes use a pure state
function and a stateless React component. Blender scenes use an event table,
scene assertions, and manifest facts.

## Build the final composition first

Render the orientation and final states before adding repeated motion. Reserve
space for the longest label, largest count, and final conclusion. Inspect the
result at full size and near feed size.

In Blender, begin with the opinionated defaults in
[the visual-direction guide](../modes/blender/references/visual-direction.md):
a three-quarter view, three depth planes, a lit and beveled stage, and a scene
archetype with enough work items to make the mechanism visible. A flat line of
boxes is not improved by rendering it in 3D.

Keep Blender's semantic labels in the scene graph. A stage or item label should
be parented to its owning mesh and rendered with normal depth and occlusion.
Only the global title or one explanatory caption may behave like HUD text.

Add one complete event next. Render frames before, during, and after its
ownership change. Expand to the full event sequence only after that event is
correct.

## Inspect fixed and continuous evidence

Capture the orientation, first completed event, peak motion, and final state.
Review these properties in order:

1. Verified story and final state.
2. Ownership and event order.
3. Counts and progress.
4. Geometry, camera, and motion paths.
5. Type, color, lighting, and polish.

Then watch the complete preview. Extract a 12 to 30 FPS strip around every
handoff shorter than 300 ms. A sparse contact sheet can miss duplication,
clipping, stale counters, or a material that changes too late.

For SVG review, run `./animation svg dev` and add `feedback=1` to the scene URL.
The reviewer seeks to a frame, clicks the relevant element, and writes a note.
The local Vite endpoint appends scene ID, delivery profile, time, scene-space
coordinates, element description, and comment to
`modes/svg/feedback/feedback.jsonl`. Treat each open JSONL record as a review
item. Fix or explicitly disposition every item before acceptance, then rerun
the semantic and media checks. The overlay is development-only and is absent
from export mode.

## Accept the video

Accept the output only when both evidence channels pass:

- model or scene assertions report no errors;
- semantic checkpoints match the visible frame;
- the expected frame sequence is complete;
- the MP4 metadata matches the render policy;
- FFmpeg decodes the complete MP4;
- the contact sheet and dense strips pass visual review;
- every open click-to-comment review item has been addressed or dispositioned;
- the final state holds long enough to read.

Keep generated frames until review passes. Do not commit frames, videos,
manifests, contact sheets, or `.blend` files.
