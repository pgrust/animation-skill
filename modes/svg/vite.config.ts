import { appendFileSync, existsSync, mkdirSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { defineConfig, type Plugin } from "vite";
import react from "@vitejs/plugin-react";

const MAX_FEEDBACK_BYTES = 64 * 1024;

function isNonEmptyString(value: unknown, maxLength: number): value is string {
  return typeof value === "string" && value.trim().length > 0 && value.length <= maxLength;
}

function parseFeedbackItem(value: unknown) {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new Error("Feedback must be a JSON object");
  }
  const item = value as Record<string, unknown>;
  const numbers = ["timeMs", "x", "y", "sceneWidth", "sceneHeight"] as const;
  if (
    !isNonEmptyString(item.id, 128)
    || !isNonEmptyString(item.sceneId, 128)
    || (item.profile !== "fast" && item.profile !== "presenter")
    || numbers.some((field) => typeof item[field] !== "number" || !Number.isFinite(item[field]))
    || (item.timeMs as number) < 0
    || (item.sceneWidth as number) <= 0
    || (item.sceneHeight as number) <= 0
    || (item.x as number) < 0
    || (item.x as number) > (item.sceneWidth as number)
    || (item.y as number) < 0
    || (item.y as number) > (item.sceneHeight as number)
    || !isNonEmptyString(item.element, 1_000)
    || !isNonEmptyString(item.comment, 4_000)
    || (item.status !== "open" && item.status !== "resolved")
    || !isNonEmptyString(item.createdAt, 64)
    || Number.isNaN(Date.parse(item.createdAt))
  ) {
    throw new Error("Feedback fields are missing or invalid");
  }
  return item;
}

function feedbackEndpoint(): Plugin {
  const directory = join(process.cwd(), "feedback");
  const file = join(directory, "feedback.jsonl");
  return {
    name: "local-animation-feedback",
    configureServer(server) {
      server.middlewares.use("/__feedback", (request, response) => {
        response.setHeader("Content-Type", "application/json; charset=utf-8");
        if (request.method === "GET") {
          const items = existsSync(file)
            ? readFileSync(file, "utf8")
                .split("\n")
                .filter(Boolean)
                .map((line) => JSON.parse(line) as unknown)
            : [];
          response.end(JSON.stringify(items));
          return;
        }
        if (request.method !== "POST") {
          response.statusCode = 405;
          response.end(JSON.stringify({ error: "method not allowed" }));
          return;
        }

        let body = "";
        let tooLarge = false;
        request.on("data", (chunk: Buffer) => {
          if (tooLarge) return;
          body += chunk.toString();
          if (Buffer.byteLength(body) > MAX_FEEDBACK_BYTES) tooLarge = true;
        });
        request.on("end", () => {
          try {
            if (tooLarge) {
              response.statusCode = 413;
              response.end(JSON.stringify({ error: "feedback body is too large" }));
              return;
            }
            const item = parseFeedbackItem(JSON.parse(body));
            mkdirSync(directory, { recursive: true });
            appendFileSync(file, `${JSON.stringify(item)}\n`, "utf8");
            response.statusCode = 201;
            response.end(JSON.stringify({ ok: true }));
          } catch (error) {
            response.statusCode = 400;
            response.end(JSON.stringify({
              error: error instanceof Error ? error.message : "invalid feedback",
            }));
          }
        });
      });
    },
  };
}

export default defineConfig({
  plugins: [react(), feedbackEndpoint()],
  server: {
    host: "127.0.0.1",
  },
});
