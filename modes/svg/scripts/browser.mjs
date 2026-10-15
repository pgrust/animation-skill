import { spawn } from "node:child_process";
import { once } from "node:events";
import { access } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { chromium } from "playwright-core";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const chromeCandidates = [
  process.env.CHROME_PATH,
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "/Applications/Chromium.app/Contents/MacOS/Chromium",
  "/usr/bin/google-chrome",
  "/usr/bin/chromium",
  "/snap/bin/chromium",
].filter(Boolean);

async function findChrome() {
  for (const candidate of chromeCandidates) {
    try {
      await access(candidate);
      return candidate;
    } catch {
      // Continue through known browser locations.
    }
  }
  throw new Error("Chrome or Chromium not found. Set CHROME_PATH to its executable.");
}

async function waitForServer(url, attempts = 100) {
  for (let attempt = 0; attempt < attempts; attempt += 1) {
    try {
      const response = await fetch(url);
      if (response.ok) return;
    } catch {
      // Vite is still starting.
    }
    await new Promise((resolvePromise) => setTimeout(resolvePromise, 100));
  }
  throw new Error(`Timed out waiting for ${url}`);
}

function waitForViteProcess(server, url) {
  return new Promise((resolvePromise, reject) => {
    let output = "";
    const timeout = setTimeout(() => {
      cleanup();
      reject(new Error(`Vite did not announce ${url}`));
    }, 10_000);
    const onData = (chunk) => {
      output += chunk.toString();
      if (output.includes(url)) {
        cleanup();
        resolvePromise();
      }
    };
    const onExit = (code) => {
      cleanup();
      reject(new Error(`Vite exited before startup with status ${code}`));
    };
    const cleanup = () => {
      clearTimeout(timeout);
      server.stdout.off("data", onData);
      server.off("exit", onExit);
    };
    server.stdout.on("data", onData);
    server.on("exit", onExit);
  });
}

export async function withAnimationPage(options, callback) {
  const port = options.port ?? Number(process.env.ANIMATION_PORT ?? 4178);
  const baseUrl = `http://127.0.0.1:${port}`;
  const scene = options.scene ?? "task-pipeline";
  const profile = options.profile ?? "fast";
  const server = spawn(
    process.execPath,
    ["node_modules/vite/bin/vite.js", "--host", "127.0.0.1", "--port", String(port), "--strictPort"],
    {
      cwd: ROOT,
      env: { ...process.env, NO_COLOR: "1" },
      stdio: ["ignore", "pipe", "pipe"],
    },
  );
  let serverError = "";
  server.stderr.on("data", (chunk) => { serverError += chunk.toString(); });

  try {
    await waitForViteProcess(server, baseUrl);
    await waitForServer(baseUrl);
    const browser = await chromium.launch({
      executablePath: await findChrome(),
      headless: true,
    });
    try {
      const page = await browser.newPage({
        viewport: { width: options.width ?? 1280, height: options.height ?? 720 },
        deviceScaleFactor: options.deviceScaleFactor ?? 1,
      });
      const url = new URL(baseUrl);
      url.searchParams.set("export", "1");
      url.searchParams.set("autoplay", "0");
      url.searchParams.set("scene", scene);
      url.searchParams.set("profile", profile);
      await page.goto(url.href, { waitUntil: "networkidle" });
      await page.waitForFunction(() => Boolean(window.__CODE_ANIMATION__));
      await page.evaluate(() => document.fonts.ready);
      const loaded = await page.evaluate(() => ({
        sceneId: window.__CODE_ANIMATION__.sceneId,
        profile: window.__CODE_ANIMATION__.profile,
        width: window.__CODE_ANIMATION__.width,
        height: window.__CODE_ANIMATION__.height,
        durationMs: window.__CODE_ANIMATION__.durationMs,
        checkpoints: window.__CODE_ANIMATION__.checkpoints,
      }));
      if (loaded.sceneId !== scene || loaded.profile !== profile) {
        throw new Error(
          `Requested ${scene}/${profile}, loaded ${loaded.sceneId}/${loaded.profile}`,
        );
      }
      await page.setViewportSize({
        width: options.width ?? loaded.width,
        height: options.height ?? loaded.height,
      });
      await callback(page, loaded);
    } finally {
      await browser.close();
    }
  } catch (error) {
    if (serverError) process.stderr.write(serverError);
    throw error;
  } finally {
    if (server.exitCode === null) {
      server.kill("SIGTERM");
      await Promise.race([
        once(server, "exit"),
        new Promise((resolvePromise) => setTimeout(resolvePromise, 1_000)),
      ]);
      if (server.exitCode === null) server.kill("SIGKILL");
    }
  }
}
