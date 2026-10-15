# Assumptions that are not universal

The repository separates mechanism from policy, but the worked example still
contains choices that can look like requirements. They are not.

## Choices the runtime makes

The runtime supports Blender 5.2.x, Eevee, PNG frame sequences, H.264 output,
and `yuv420p`. Configuration makes resolution, samples, frame range, FPS, AgX
look, CRF, and encoder preset explicit.

These limits keep the interface honest. Cycles, Workbench, Blender 6, alpha
video, audio, and alternate codecs need code and tests. Changing a string in
`project.json` is not enough.

## Opinionated starting defaults

New projects deliberately start with a three-quarter camera, three-point
lighting, multiple depth lanes, a neutral high-contrast palette, and enough
overlapping work items to reveal a mechanism. Semantic labels start attached to
their owning scene objects instead of in a camera-space overlay. These are
strong creative defaults, not universal technical requirements. They prevent a
fresh scene from collapsing into one cube moving through a row of boxes or a
3D stage covered by flat HUD text.

The visual-direction guide explains when and how to replace them. Preserve the
underlying tests: readable ownership, visible depth, feed-size legibility, a
complete final state, and motion that communicates cause.

## Choices the worked example makes

The parcel sorter uses:

- a fixed orthographic camera
- 30 FPS
- 640×360 at 12 samples for preview
- 1280×720 at 32 samples for final output
- AgX Medium High Contrast
- one warm key, one cool fill, and one colored rim light
- a dark neutral set with teal and orange route colors
- Blender's built-in font
- no depth of field, motion blur, audio, imported assets, or compositing

These choices fit that short technical explainer. The generated starter is
richer and uses a mild semantic camera reframe. Neither example defines a
brand. A product demo, character scene, scientific visualization, or cinematic
walkthrough needs a different camera, lighting, assets, and review contract.

## Choices that often hide inside copied scripts

Treat these values as suspect when adapting the example:

- `ortho_scale` encodes this set's projected bounds and aspect ratio.
- Light energy depends on scene scale, material response, exposure, and emitter size.
- Text positions depend on font metrics and camera rotation.
- Bevel width depends on object scale.
- Thirty FPS affects every frame number in the event table.
- Thirty-two Eevee samples passed this example but are not a quality threshold.
- H.264 and `yuv420p` target ordinary playback, not archival masters or alpha.
- A fixed camera improves comparisons but can weaken spatial storytelling.
- Disabled depth of field and motion blur protect ownership clarity in this example.

Move these decisions into project data when a second real project needs a
different value. Do not add configuration for hypothetical variation.

## Performance claims

This repository does not publish a render-time promise. Render time depends on
the host GPU, Blender build, scene complexity, resolution, samples, shadows,
ray tracing, and effects.

The current recommendation to start at 32 Eevee samples is a tested working
point, not a controlled 32-versus-64 benchmark. Compare one difficult frame at
delivery size before paying for more samples.

Eevee is not always faster. A headless Linux host using software rasterization
can make CPU Cycles faster for small scenes. Benchmark the target host.

## Platform dependencies

The project command requires `blender`, `ffmpeg`, `ffprobe`, and Python 3.11 or
newer on `PATH`. The worked example uses no system font and no imported asset.
That avoids two common cross-machine failures.

The shell adapter uses Bash. The Python runner performs all path handling,
cleanup, rendering, encoding, and verification so a future Windows adapter can
call the same command logic without changing scene files.
