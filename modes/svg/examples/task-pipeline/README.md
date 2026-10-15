# Task pipeline example

This example shows six jobs move from a queue through a check stage and into a
committed state. Each job keeps one ID and one owner. The moving cards, counts,
progress bar, checkpoints, and final state come from one event model.

Source files:

- `src/scenes/task-pipeline/model.ts` contains events, profiles, state, inspection, and validation.
- `src/scenes/task-pipeline/TaskPipelineAnimation.tsx` contains SVG presentation.
- `src/scenes/index.tsx` registers the example with the runtime.

From `modes/svg/`, run the complete example:

```bash
npm install
npm run check
npm run capture:checkpoints -- --scene task-pipeline --profile fast
npm run render:video -- --scene task-pipeline --profile fast --output output/task-pipeline-fast.mp4
npm run contact-sheet -- --input output/task-pipeline-fast.mp4 --output output/task-pipeline-fast-contact-sheet.png
```

Read [EVAL.md](EVAL.md) for the verified story, render evidence, iteration log,
and limits.
