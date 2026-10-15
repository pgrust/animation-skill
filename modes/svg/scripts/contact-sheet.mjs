import { mkdir } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { numberOption, option, positiveIntegerOption } from "./cli.mjs";
import { probeVideo, run } from "./media.mjs";

const input = resolve(option("input", "output/task-pipeline-fast.mp4"));
const output = resolve(option("output", "output/task-pipeline-fast-contact-sheet.png"));
const sampleFps = numberOption("sample-fps", 1.5);
const columns = positiveIntegerOption("columns", 6);
if (sampleFps <= 0) throw new Error("--sample-fps must be positive");

const metadata = await probeVideo(input);
const duration = Number(metadata.format?.duration);
if (!Number.isFinite(duration) || duration <= 0) {
  throw new Error(`Could not read a positive duration from ${input}`);
}
const sampleCount = Math.max(1, Math.ceil(duration * sampleFps));
const rows = Math.ceil(sampleCount / columns);
await mkdir(dirname(output), { recursive: true });
await run("ffmpeg", [
  "-y", "-v", "error",
  "-i", input,
  "-vf", `fps=${sampleFps},scale=480:-1,tile=${columns}x${rows}:padding=4:margin=4`,
  "-frames:v", "1",
  "-update", "1",
  output,
]);
process.stdout.write(`${output} (${columns}x${rows}, ${sampleCount} samples)\n`);
