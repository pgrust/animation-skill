# Blender 5.2 failure modes

## Correct scene, bland result

| Symptom | Cause | Recovery |
| --- | --- | --- |
| One object slides through a row of labeled boxes | The event table was copied literally into geometry without choosing a 3D archetype | Use the queue/pool, parallel pipeline, fan-out/merge, before/after, or bank/gate/rack archetype; otherwise switch to SVG |
| Motion reads as flat despite 3D geometry | Camera is front-on or every object shares one plane | Start with `add_three_quarter_camera`, stagger stations in depth, and require visible top, front, and side faces |
| Viewer cannot see concurrency | Too few work items or uniformly serialized timing | Use 6 to 12 persistent items and overlap 2 to 4 at the peak when the mechanism is genuinely concurrent |
| Camera moves but the explanation does not improve | A constant orbit was added as decoration | Hold during handoffs and use no more than two short reframes that reveal scale, depth, or the final state |
| Scene looks like luminous SVG cards | Frontal lighting, emissive panels, and no bevels erased surface form | Use the three-point rig, bevel important edges, keep the world dim, and reserve emission for state |
| Animation starts immediately and ends on arrival | No orient or landing beat was budgeted | Use orient, demonstrate, accelerate, and land; reserve at least 1.5 seconds for the final hold |

Passing scene assertions proves correctness, not visual usefulness. Apply the
[visual-direction gate](visual-direction.md#validate-the-visual-design) before
starting a master render.

## Camera and text

| Symptom | Cause | Recovery |
| --- | --- | --- |
| Stage or node labels look pasted over the finished video | Semantic text was placed in camera space, parented to the camera, or treated as HUD text | Parent it to the owning mesh with `add_attached_label`; use a surface label first and an object-anchored billboard only when necessary |
| Label stays in one screen position while its object or camera moves | Label has no semantic parent | Attach it to the owner and inspect the parent relationship in the scene graph |
| Surface label flickers or disappears at an angle | Text lies exactly on the surface or is too small for the projected face | Offset it 0.02–0.06 units, enlarge the owning face or label, and render the most oblique final-resolution frame |
| Object color change destroys label contrast | Label relies on the object's animated material for contrast | Add a stable inset plate or use the opposite neutral text color |
| Header or work area clips despite plausible world dimensions | `Camera.ortho_scale` was chosen without checking projected bounds | Render a cold checkpoint, measure in the camera basis, then change only camera scale or target |
| Long labels appear truncated against their panels | A billboard aimed at the camera position under an orthographic camera | Copy the orthographic camera rotation so the text plane stays parallel to the image plane |
| Text looks soft at preview size but disappears in the master | Low resolution hid a geometry intersection | Render the longest and smallest labels at final resolution before locking typography |
| Text metrics change on another machine | The scene used a system font that is missing or has different metrics | Ship a licensed font or use Blender's built-in font and recheck layout |

Do not aim orthographic billboards at the camera position. Orthographic rays are
parallel, so every billboard uses the same rotation.

## Materials and animation

| Symptom | Cause | Recovery |
| --- | --- | --- |
| Several movers activate together | The movers share one material data block | Create one material per independently animated mover |
| Checkpoint stills pass but movers stay dark during travel | The sampled frames missed the activation interval | Render and watch the complete preview timeline |
| Objects overshoot or reverse near a key | Unclamped Bezier handles crossed the intended path | Use `AUTO_CLAMPED`, `LINEAR`, or `CONSTANT` interpolation based on the state change |
| Old code raises an attribute error for `action.fcurves` | Blender 5 uses layered Actions | Walk layers, keyframe strips, channel bags, f-curves, and keyframe points |

`blender_animation.scene.set_interpolation()` contains the supported Blender 5.2
Action traversal.

## Headless execution

| Symptom | Cause | Recovery |
| --- | --- | --- |
| `ModuleNotFoundError: No module named 'blender_animation'` | Blender ignored or did not inherit the expected Python path | Use `scripts/render_project.py`, which inserts the repository root before loading `build.py` |
| `poll() failed, context is incorrect` | A `bpy.ops` call depends on selection, mode, area, or editor state | Prefer `bpy.data`. Keep unavoidable primitive operators inside helpers that capture and name the result immediately. |
| A rerun contains duplicate objects or stale handlers | The script reused a live Blender process without full cleanup | Start each source revision with `--factory-startup` in a fresh process |
| Python traceback appears but automation reports success | Blender returned zero after a script exception | Keep `--python-exit-code 1` in the command |

## Rendering and video

| Symptom | Cause | Recovery |
| --- | --- | --- |
| A failed render destroys the only movie | Blender encoded directly to a video container | Render PNG frames first, then encode with FFmpeg |
| The MP4 opens but ends early | The encoder received an incomplete sequence | Require the exact configured frame filenames before encoding |
| `No such filter: 'drawtext'` | The local FFmpeg build omitted `drawtext` | Keep labels in the scene or stack images without `drawtext` |
| ffprobe passes while the story is wrong | Media metadata cannot see event order or label overlap | Pair the manifest and media checks with actual pixel review |

## Blender version changes

Blender 5.2 prints deprecation warnings for `World.use_nodes` and
`Material.use_nodes`. The calls still work in 5.2. Do not silence the warnings
and claim Blender 6 support. Port the node setup against Blender 6, then run the
worked example and the complete visual gate before changing the supported
version.
