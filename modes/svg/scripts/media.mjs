import { spawn } from "node:child_process";
import { readFile } from "node:fs/promises";

export function run(command, args, { capture = false } = {}) {
  return new Promise((resolvePromise, reject) => {
    const child = spawn(command, args, {
      stdio: capture ? ["ignore", "pipe", "pipe"] : "inherit",
    });
    let stdout = "";
    let stderr = "";
    if (capture) {
      child.stdout.on("data", (chunk) => { stdout += chunk.toString(); });
      child.stderr.on("data", (chunk) => { stderr += chunk.toString(); });
    }
    child.on("error", reject);
    child.on("exit", (code) => {
      if (code === 0) resolvePromise({ stdout, stderr });
      else reject(new Error(`${command} exited with status ${code}${stderr ? `: ${stderr}` : ""}`));
    });
  });
}

function rateAsNumber(value) {
  const [numerator, denominator = "1"] = String(value).split("/").map(Number);
  return numerator / denominator;
}

export async function probeVideo(path) {
  const result = await run("ffprobe", [
    "-v", "error",
    "-show_entries",
    "format=duration,size:stream=codec_name,width,height,pix_fmt,r_frame_rate,nb_frames,color_space,color_transfer,color_primaries",
    "-of", "json",
    path,
  ], { capture: true });
  return JSON.parse(result.stdout);
}

export async function verifyVideo(path, expected) {
  const metadata = await probeVideo(path);
  const streams = metadata.streams ?? [];
  if (streams.length !== 1) throw new Error(`Expected one video stream, found ${streams.length}`);
  const stream = streams[0];
  const checks = {
    codec_name: "h264",
    width: expected.width,
    height: expected.height,
    pix_fmt: "yuv420p",
    nb_frames: String(expected.frameCount),
  };
  for (const [key, value] of Object.entries(checks)) {
    if (String(stream[key]) !== String(value)) {
      throw new Error(`Expected ${key}=${value}, got ${stream[key]}`);
    }
  }
  if (Math.abs(rateAsNumber(stream.r_frame_rate) - expected.fps) > 0.0001) {
    throw new Error(`Expected ${expected.fps} FPS, got ${stream.r_frame_rate}`);
  }
  const expectedDuration = expected.frameCount / expected.fps;
  const duration = Number(metadata.format?.duration);
  const tolerance = Math.max(0.05, 1 / expected.fps);
  if (!Number.isFinite(duration) || Math.abs(duration - expectedDuration) > tolerance) {
    throw new Error(`Expected duration ${expectedDuration.toFixed(3)}, got ${duration}`);
  }
  await run("ffmpeg", ["-v", "error", "-i", path, "-f", "null", "-"]);
  return metadata;
}

export async function readRenderManifest(path) {
  return JSON.parse(await readFile(path, "utf8"));
}
