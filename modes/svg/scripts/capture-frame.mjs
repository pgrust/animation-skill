import { mkdir } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { withAnimationPage } from "./browser.mjs";
import { numberOption, option } from "./cli.mjs";

const scene = option("scene", "task-pipeline");
const profile = option("profile", "fast");
const timeSeconds = numberOption("time", 0);
const output = resolve(option("output", `output/${scene}-${profile}-${timeSeconds.toFixed(2)}s.png`));
const width = numberOption("width", 1280);
const height = numberOption("height", 720);

await mkdir(dirname(output), { recursive: true });
await withAnimationPage({ scene, profile, width, height }, async (page, loaded) => {
  const timeMs = timeSeconds * 1000;
  if (timeMs < 0 || timeMs > loaded.durationMs) {
    throw new Error(`--time must be between 0 and ${(loaded.durationMs / 1000).toFixed(3)}`);
  }
  await page.evaluate((nextTimeMs) => window.__CODE_ANIMATION__.setTime(nextTimeMs), timeMs);
  await page.screenshot({ path: output, type: "png" });
});

process.stdout.write(`${output}\n`);
