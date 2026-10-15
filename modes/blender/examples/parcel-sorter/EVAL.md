# Parcel sorter evaluation

Status: Pass. The example renders from a clean Blender 5.2 process, preserves
its event table, and passes frame-sequence, manifest, media, decode, and visual
checks.

## Verified story

Teaching sentence: A parcel keeps its identity while one routing decision
changes its destination.

The source and generated manifest preserve these facts:

- P1 starts first, takes Route A, and finishes in Bin A.
- P2 starts second, takes Route B, and finishes in Bin B.
- P3 starts third, takes Route A, and finishes in Bin A.
- Every parcel crosses the routing gate once.
- The final Bin A order is P1 and P3. Bin B contains P2.
- The timeline contains 150 frames at 30 FPS.

The conveyor shape, path curves, colors, frame spacing, and lighting are
illustrative. They do not model a particular sorting machine or measured
throughput.

## Visual result

The fixed orthographic camera keeps parcel size stable and shows both routes at
once. Route color activates on each moving parcel, while labels preserve P1,
P2, and P3 identity. The contact sheet shows the input, routing decisions, and
final bins without narration.

The example favors mechanism clarity over realism. The parcels float slightly
above the rails, the routing gate is symbolic, and the paths do not represent a
physical conveyor junction.

## Iteration record

| Pass | Evidence | Problem | Correction |
| ---: | --- | --- | --- |
| 1 | Frames 1, 76, and 150 at 640×360 | The title clipped above the frame. Parcel IDs appeared far from their bodies. | Increased orthographic coverage, moved the title down, and fixed parent transforms with `matrix_parent_inverse`. |
| 2 | Frames 1, 76, and 150 after the transform fix | IDs followed their parcels, but the input label competed with the queue. | Moved the input label into reserved empty space. |
| 3 | Complete 150-frame preview and eight-sample contact sheet | Event order, route activation, final ownership, and final hold passed. | Locked the scene for the master. |

The parent-transform failure matters beyond this example. A child can look
correct at its starting frame and drift by the parent's full initial offset
after animation. Check child world coordinates at the final frame when a label
or ornament follows a moving root.

## Verification

These commands passed:

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile blender_animation/*.py scripts/*.py examples/parcel-sorter/build.py
bash -n examples/parcel-sorter/render.sh
examples/parcel-sorter/render.sh check
examples/parcel-sorter/render.sh preview 1 76 150
examples/parcel-sorter/render.sh timeline
examples/parcel-sorter/render.sh final
examples/parcel-sorter/render.sh contact-sheet
```

The final video reports H.264, 1280×720, `yuv420p`, 30 FPS, 150 frames, and
5.000 seconds. FFmpeg decoded the complete file without an error. The runner
found exactly 150 final PNG files and no extra frame filename.

One repeated `final` run took 30.80 seconds end to end on a MacBook Pro with an
Apple M5 Pro and 48 GB memory. Blender reported 29.399 seconds for scene build
and frame rendering; encoding and verification used the remainder. This is one
observation with Blender 5.2.1 LTS and FFmpeg 8.1.2, not a cross-scene or
cross-platform benchmark.

Generated videos, frames, the `.blend` file, the manifest, and the contact
sheet remain under ignored `output/` paths.

## Limits

- The example tests Eevee only. It contains no controlled Eevee-versus-Cycles comparison.
- It tests Blender 5.2.1. Blender 6 compatibility is unknown.
- Blender 5.2 warns that `World.use_nodes` and `Material.use_nodes` will change in Blender 6.
- Built-in font metrics are portable across Blender installs but visually plain.
- The scene has no audio, narration, imported asset, camera move, transparency, depth of field, or motion blur.
- The example does not establish a render-time expectation for other hardware or scenes.
