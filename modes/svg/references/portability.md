# Tested behavior and local choices

## Supported behavior

The repository supports React 19, TypeScript 7, Vite 8, SVG scenes, Chrome or
Chromium capture, and H.264 video through FFmpeg. Node.js must be 22.12 or newer.

macOS and Linux browser paths are present in `scripts/browser.mjs`. Only macOS
has been tested. Windows needs a browser-path adapter and shell-command review.

## Worked-example choices

The task-pipeline example uses these local choices:

- a fixed 1280 by 720 view box;
- a dark neutral canvas;
- gray queued jobs, blue active jobs, and green committed jobs;
- six jobs with text payloads;
- straight horizontal travel;
- `fast` and `presenter` pacing profiles;
- system sans-serif and monospace fonts;
- no audio, narration, imported assets, or responsive scene reflow.

These choices fit one flat mechanism. They do not define a visual identity or a
required animation style.

## Choices that can look like requirements

- **1280 by 720:** a tested output size, not a required canvas.
- **30 FPS:** adequate for this motion, not a universal frame rate.
- **CRF 18 and the `medium` preset:** delivery policy, not a quality threshold.
- **H.264 and `yuv420p`:** common playback output, not an archival or alpha format.
- **BT.709 metadata:** appropriate for this video path, not browser color proof.
- **Fixed camera and panels:** useful for comparison, but restrictive for maps or zoomable systems.
- **Fast and presenter profiles:** two useful pacing contracts, not channel names or global speed ratios.
- **System fonts:** dependency-free, but metrics vary by operating system.
- **SVG:** inspectable and accessible for small semantic scenes, but inefficient for dense particles.
- **Chrome screenshots:** deterministic on the tested host, but not proof of identical Safari or Firefox rendering.

Move a choice into shared configuration only after a second real scene needs a
different value. Do not add options for hypothetical variation.

## Performance

Render time depends on frame count, viewport, SVG complexity, filters, browser,
encoder settings, and hardware. The worked example records one local run. It is
not a performance promise.

Blur and glow filters can dominate screenshot cost. Test the hardest frame at
delivery size before adding filters across many objects.
