# Parcel sorter worked example

This project renders a five-second headless Blender animation. Three named
parcels enter one routing gate. P1 and P3 take Route A. P2 takes Route B. Every
parcel keeps its identity through the transfer.

From `modes/blender/`, run the complete workflow:

```bash
examples/parcel-sorter/render.sh check
examples/parcel-sorter/render.sh preview 1 76 150
examples/parcel-sorter/render.sh timeline
examples/parcel-sorter/render.sh final
examples/parcel-sorter/render.sh contact-sheet
```

`project.json` defines the 150-frame timeline and render policy. `build.py`
defines the event table, scene, animation, assertions, and manifest facts.
`render.sh` delegates to the shared runner.

Generated output stays under `output/` and does not enter Git.

Read [EVAL.md](EVAL.md) for the verified story, iteration record, and limits.
