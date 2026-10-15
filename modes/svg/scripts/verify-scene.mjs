import { withAnimationPage } from "./browser.mjs";
import { option } from "./cli.mjs";

const scene = option("scene", "task-pipeline");
const requestedProfile = option("profile", "all");
const profiles = requestedProfile === "all" ? ["fast", "presenter"] : [requestedProfile];
const results = [];

for (let index = 0; index < profiles.length; index += 1) {
  const profile = profiles[index];
  await withAnimationPage({ scene, profile, port: 4178 + index }, async (page, loaded) => {
    const validationErrors = await page.evaluate(() => window.__CODE_ANIMATION__.validate());
    if (validationErrors.length > 0) {
      throw new Error(`${scene}/${profile} model validation failed:\n${validationErrors.join("\n")}`);
    }
    const checkpoints = [];
    for (const checkpoint of loaded.checkpoints) {
      if (checkpoint.timeMs < 0 || checkpoint.timeMs > loaded.durationMs) {
        throw new Error(`Checkpoint ${checkpoint.id} is outside the timeline`);
      }
      const snapshot = await page.evaluate(
        (timeMs) => window.__CODE_ANIMATION__.inspect(timeMs),
        checkpoint.timeMs,
      );
      checkpoints.push({ ...checkpoint, snapshot });
    }
    results.push({ scene, profile, durationMs: loaded.durationMs, checkpoints });
  });
}

process.stdout.write(`${JSON.stringify(results, null, 2)}\n`);
