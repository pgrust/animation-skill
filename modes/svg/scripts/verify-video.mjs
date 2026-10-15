import { resolve } from "node:path";
import { option } from "./cli.mjs";
import { readRenderManifest, verifyVideo } from "./media.mjs";

const input = resolve(option("input", "output/task-pipeline-fast.mp4"));
const manifestPath = resolve(option("manifest", `${input}.json`));
const manifest = await readRenderManifest(manifestPath);
const metadata = await verifyVideo(input, manifest);
process.stdout.write(`VIDEO_VERIFY=${JSON.stringify(metadata)}\n`);
