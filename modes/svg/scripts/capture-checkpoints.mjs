import { mkdir, readdir, unlink, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { withAnimationPage } from "./browser.mjs";
import { numberOption, option } from "./cli.mjs";

const scene = option("scene", "task-pipeline");
const profile = option("profile", "fast");
const outputDir = resolve(option("output-dir", `output/checkpoints/${scene}-${profile}`));
const width = numberOption("width", 1280);
const height = numberOption("height", 720);
const manifest = [];

await mkdir(outputDir, { recursive: true });
for (const filename of await readdir(outputDir)) {
  if (filename.startsWith("checkpoint-") && filename.endsWith(".png")) {
    await unlink(resolve(outputDir, filename));
  }
}
await withAnimationPage({ scene, profile, width, height }, async (page, loaded) => {
  for (const checkpoint of loaded.checkpoints) {
    await page.evaluate((timeMs) => window.__CODE_ANIMATION__.setTime(timeMs), checkpoint.timeMs);
    const snapshot = await page.evaluate(() => window.__CODE_ANIMATION__.inspect());
    const filename = `checkpoint-${checkpoint.id}.png`;
    await page.screenshot({ path: resolve(outputDir, filename), type: "png" });
    manifest.push({ ...checkpoint, filename, snapshot });
  }
});
const actualImages = (await readdir(outputDir))
  .filter((filename) => filename.startsWith("checkpoint-") && filename.endsWith(".png"))
  .sort();
const expectedImages = manifest.map((entry) => entry.filename).sort();
if (actualImages.length !== expectedImages.length ||
    actualImages.some((filename, index) => filename !== expectedImages[index])) {
  throw new Error("Checkpoint image set does not match the scene checkpoint list");
}
await writeFile(
  resolve(outputDir, "checkpoints.json"),
  `${JSON.stringify({ scene, profile, width, height, checkpoints: manifest }, null, 2)}\n`,
);
process.stdout.write(`${outputDir}\n`);
