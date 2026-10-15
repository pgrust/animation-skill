# Runtime and scene reference

## Supported environment

| Item | Supported value |
| --- | --- |
| Node.js | 22.12 or newer |
| UI runtime | React 19, TypeScript 7, Vite 8 |
| Drawing model | SVG |
| Capture browser | Google Chrome or Chromium through `playwright-core` |
| Video tools | FFmpeg and FFprobe |
| Video output | H.264, `yuv420p`, BT.709 metadata |

## Scene interface

`src/runtime/scene.ts` defines `SceneDefinition`. A scene supplies:

- `id` and `title`;
- native `width` and `height`;
- supported delivery profiles;
- `durationMs(profile)`;
- named `checkpoints(profile)`;
- `inspect(timeMs, profile)` for JSON-compatible model evidence;
- `validate(profile)` for semantic errors;
- `render(timeMs, profile)` for the React tree.

`src/scenes/index.tsx` is the registry. The runtime rejects unknown scene IDs
and unsupported profiles before rendering.

## Browser interface

`src/App.tsx` exposes `window.__CODE_ANIMATION__` after the scene loads:

```ts
{
  sceneId: string;
  profile: "fast" | "presenter";
  width: number;
  height: number;
  durationMs: number;
  checkpoints: Checkpoint[];
  getTime(): number;
  setTime(timeMs: number): void;
  play(): void;
  pause(): void;
  inspect(timeMs?: number): Record<string, unknown>;
  validate(): string[];
}
```

Capture scripts load `?export=1&autoplay=0`, wait for this interface, verify the
requested scene and profile, wait for browser fonts, and then seek explicitly.
They never depend on wall-clock playback.

The interactive preview accepts `t=<milliseconds>` for an exact paused frame.
This is useful when sharing or reopening a review note without replaying to the
same point.

## Local feedback interface

Start the Vite preview with `./animation svg dev`, then add `feedback=1` to the
scene URL. The overlay pauses playback when the reviewer clicks, records the
current scene, profile, time, scene-space coordinates, and nearby SVG element,
and sends the note to the development-only `/__feedback` endpoint. Vite appends
one JSON object per line to `feedback/feedback.jsonl` inside `modes/svg/`.

The endpoint binds through the local Vite server, validates request shape and
size, and is not part of a production build. `feedback/` is ignored by Git so
private review notes do not enter a release by accident. Export mode does not
enable the overlay.

## Model and SVG split

The task-pipeline model owns the event table, timing profiles, task phases,
counts, completion, checkpoints, structured snapshots, and semantic validation.
The SVG scene owns coordinates, panels, colors, type, and shapes.

The SVG scene may interpolate positions from model progress. It must not infer
ownership, completion, or event order from coordinates.

## Output contract

Generated files live under `output/` and remain ignored by Git. A video render
writes:

```text
output/<name>.mp4
output/<name>.mp4.json
```

The sidecar manifest records the scene, profile, dimensions, FPS, exact frame
count, scene duration, encoded duration, codec policy, and checkpoints.

`scripts/render-video.mjs` renders into a fresh temporary directory. The script
requires every zero-based PNG filename before encoding. It retains the frame
directory after failure and removes it only after the video passes verification.
