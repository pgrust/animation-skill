# React and SVG animation failure modes

## State and timing

| Symptom | Cause | Recovery |
| --- | --- | --- |
| Preview looks right, but an exported frame differs | CSS animation or a browser clock owns part of the state | Derive the full visual tree from `getState(timeMs, profile)` and seek through the browser interface |
| Counter disagrees with visible objects | The component computes counters separately from movers | Return both from one event model |
| One object appears twice during a handoff | Source and destination use independent visibility conditions | Give the object one phase and render one SVG owner |
| Presenter cut teaches a different sequence | Two profiles maintain separate event schedules | Keep one event table and vary phase durations only |
| Fast cut makes the first operation unreadable | A global video speed filter compressed every phase | Shorten repeated work and holds without removing the first full event |

## Capture and browser control

| Symptom | Cause | Recovery |
| --- | --- | --- |
| Every screenshot shows the default scene | A query parameter was dropped or ignored | Verify loaded `sceneId` and `profile` before capture |
| Text shifts between captures | The screenshot starts before fonts settle or uses a missing system font | Wait for `document.fonts.ready`; ship a licensed font when exact metrics matter |
| Headless capture cannot start | Chrome is outside the known paths | Set `CHROME_PATH` to the Chrome or Chromium executable |
| A rerun leaves misleading checkpoint files | Filenames depend on checkpoint order and old files remain | Use stable `checkpoint-<id>.png` names, clean only that namespace, and require the exact set |
| Vite starts, but the script captures another server | A fixed port is already occupied and polling accepts the old process | Require the new Vite child to announce its URL; change `ANIMATION_PORT` when the port is busy |
| Feedback mode says the endpoint is unavailable | The page came from a static build or a server other than this repo's Vite config | Run `./animation svg dev` and open its local URL with `feedback=1` |
| A feedback pin appears in the wrong place | The scene's native dimensions and displayed SVG geometry disagree | Keep the scene definition width and height equal to the SVG view box; pins are stored in scene-space coordinates |

The worked example exposed the stale-checkpoint failure. An early run named
files by list position. Reordering semantic checkpoints left old PNGs beside
new PNGs. The current script uses checkpoint IDs and verifies the resulting set.

## SVG composition

| Symptom | Cause | Recovery |
| --- | --- | --- |
| A moving object vanishes under a panel | SVG paint order does not match semantic ownership | Render structural surfaces before moving work; use a narrow mask only for a real aperture |
| A mover bends around a label | Composition changed the implied data path | Move the label or panel; keep the technical path honest |
| Final values look off-center | Space reserved for temporary arithmetic remains after commit | Return settled text to its optical center |
| Labels pass checkpoint review but clip during motion | Sparse checkpoints miss the widest moving state | Inspect worst-case data and a dense transition strip |
| Glow makes text unreadable at feed size | Active styling covers the information layer | Keep glow behind the card and inspect near 640 pixels wide |

## Video output

| Symptom | Cause | Recovery |
| --- | --- | --- |
| MP4 ends before the final hold | Frame count used rounded duration or a partial sequence | Use `ceil(duration × FPS)` and require exact filenames before encoding |
| MP4 opens but contains a damaged frame | Metadata inspection checks only the container | Decode the complete video with FFmpeg |
| Failed render leaves no evidence | A cleanup block deletes temporary frames unconditionally | Remove temporary frames only after verification passes |
| Contact sheet looks correct while a handoff flashes | Low sample rate skips the short error | Render a dense strip around the handoff |
