# Task pipeline evaluation

Status: Pass. Both profiles preserve the event model and pass source, model,
frame-sequence, media, decode, and visual checks.

## Verified story

The example demonstrates one claim: a job keeps its identity while ownership
changes from queued to in flight to committed.

The model and checkpoint snapshots preserve these facts:

- J1 through J6 start in the queue.
- Jobs start and commit in ID order.
- Every job has one phase at each sampled time.
- Queued, in-flight, and committed counts always total six.
- The committed count never decreases.
- Both profiles end with J1 through J6 committed.

Payload names, stage duration, overlap, straight paths, colors, and the check
operation are illustrative. They do not represent measured throughput or a
specific production system.

## Iteration record

| Pass | Evidence | Problem | Correction |
| ---: | --- | --- | --- |
| 1 | TypeScript build, model tests, and browser snapshots | Module-scope scene narrowing failed inside React closures. Peak motion occurred before the first commit, but checkpoint files listed the reverse order. | Added typed scene and profile loaders. Reordered checkpoints by time. |
| 2 | Four 1280 by 720 checkpoint images | Composition, labels, counts, and final state were readable. A rerun retained old position-numbered checkpoint PNGs. | Switched to stable checkpoint-ID filenames, scoped cleanup, and an exact output-set check. |
| 3 | Both full MP4s, two contact sheets, and a 20 FPS first-commit strip | Ownership passed, but a filter on the parent group gave idle cards an active glow. | Applied the glow filter only to active cards. |
| 4 | Rebuilt checkpoints and both complete MP4s | No duplicate card, missing owner, stale counter, clipping, idle glow, or final-state drift appeared. | Locked the worked example. |

## Verification

These commands passed:

```bash
npm run build
npm test
npm run verify:scene
npm run capture:checkpoints -- --scene task-pipeline --profile fast
npm run render:video -- --scene task-pipeline --profile fast --output output/task-pipeline-fast.mp4
npm run render:video -- --scene task-pipeline --profile presenter --output output/task-pipeline-presenter.mp4
npm run verify:video -- --input output/task-pipeline-fast.mp4
npm run verify:video -- --input output/task-pipeline-presenter.mp4
```

The fast MP4 reports H.264, 1280 by 720, `yuv420p`, BT.709, 30 FPS, 182
frames, and 6.067 seconds. The final repeated command took 8.11 seconds.

The presenter MP4 reports H.264, 1280 by 720, `yuv420p`, BT.709, 30 FPS, 336
frames, and 11.2 seconds. The final repeated command took 8.18 seconds.

Both measurements came from a MacBook Pro with an Apple M5 Pro and 48 GB of
memory. They are observations, not cross-scene or cross-platform benchmarks.

Generated checkpoints, videos, manifests, contact sheets, and dense strips
remain under ignored `output/` paths.

## Limits

- Only Chrome and macOS were tested.
- The example does not test a second registered scene.
- System font metrics can differ across platforms.
- The example contains no audio, narration, Canvas, imported asset, responsive scene layout, or alpha video.
- Structured validation proves event facts. It cannot prove label readability or visual hierarchy.
