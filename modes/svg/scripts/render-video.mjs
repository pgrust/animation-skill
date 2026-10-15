import { mkdtemp, mkdir, readdir, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { withAnimationPage } from "./browser.mjs";
import { numberOption, option, positiveIntegerOption } from "./cli.mjs";
import { run, verifyVideo } from "./media.mjs";

const scene = option("scene", "task-pipeline");
const profile = option("profile", "fast");
const output = resolve(option("output", `output/${scene}-${profile}.mp4`));
const width = positiveIntegerOption("width", 1280);
const height = positiveIntegerOption("height", 720);
const fps = positiveIntegerOption("fps", 30);
const crf = numberOption("crf", 18);
const preset = option("preset", "medium");

if (width % 2 !== 0 || height % 2 !== 0) {
  throw new Error("--width and --height must be even for yuv420p");
}
if (crf < 0 || crf > 51) throw new Error("--crf must be between 0 and 51");

await mkdir(dirname(output), { recursive: true });
const frames = await mkdtemp(join(tmpdir(), "react-svg-animation-"));
let succeeded = false;

try {
  let durationMs = 0;
  let checkpoints = [];
  await withAnimationPage({ scene, profile, width, height }, async (page, loaded) => {
    durationMs = loaded.durationMs;
    checkpoints = loaded.checkpoints;
    const validationErrors = await page.evaluate(() => window.__CODE_ANIMATION__.validate());
    if (validationErrors.length > 0) {
      throw new Error(`Model validation failed:\n${validationErrors.join("\n")}`);
    }
    const frameCount = Math.ceil((durationMs / 1000) * fps);
    for (let frame = 0; frame < frameCount; frame += 1) {
      const timeMs = (frame / fps) * 1000;
      await page.evaluate((nextTimeMs) => window.__CODE_ANIMATION__.setTime(nextTimeMs), timeMs);
      await page.screenshot({
        path: join(frames, `${String(frame).padStart(5, "0")}.png`),
        type: "png",
      });
    }
  });

  const frameCount = Math.ceil((durationMs / 1000) * fps);
  const actualNames = (await readdir(frames)).filter((name) => name.endsWith(".png")).sort();
  const expectedNames = Array.from(
    { length: frameCount },
    (_, frame) => `${String(frame).padStart(5, "0")}.png`,
  );
  if (actualNames.length !== expectedNames.length ||
      actualNames.some((name, index) => name !== expectedNames[index])) {
    throw new Error(`Frame sequence is incomplete: expected ${frameCount}, found ${actualNames.length}`);
  }
  process.stdout.write(`FRAME_SEQUENCE=${frameCount} complete frames in ${frames}\n`);

  await run("ffmpeg", [
    "-y", "-v", "warning",
    "-framerate", String(fps),
    "-start_number", "0",
    "-i", join(frames, "%05d.png"),
    "-c:v", "libx264",
    "-preset", preset,
    "-crf", String(crf),
    "-tune", "animation",
    "-color_primaries", "bt709",
    "-color_trc", "bt709",
    "-colorspace", "bt709",
    "-pix_fmt", "yuv420p",
    "-movflags", "+faststart",
    output,
  ]);

  const manifest = {
    schemaVersion: 1,
    scene,
    profile,
    width,
    height,
    fps,
    frameCount,
    sceneDurationMs: durationMs,
    encodedDurationSeconds: frameCount / fps,
    codec: "h264",
    pixelFormat: "yuv420p",
    crf,
    preset,
    checkpoints,
  };
  const manifestPath = `${output}.json`;
  await writeFile(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`);
  const metadata = await verifyVideo(output, manifest);
  process.stdout.write(`VIDEO_VERIFY=${JSON.stringify(metadata)}\n`);
  process.stdout.write(`VIDEO=${output}\nMANIFEST=${manifestPath}\n`);
  succeeded = true;
} finally {
  if (succeeded) {
    await rm(frames, { recursive: true, force: true });
  } else {
    process.stderr.write(`Render failed. Retained frame directory: ${frames}\n`);
  }
}
