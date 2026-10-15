import { access, mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

function option(name) {
  const index = process.argv.indexOf(`--${name}`);
  return index >= 0 ? process.argv[index + 1] : undefined;
}

function positionalName() {
  const args = process.argv.slice(2);
  return args.find((value, index) => !value.startsWith("--") && args[index - 1] !== "--name");
}

function pascalCase(value) {
  return value
    .split(/[^a-zA-Z0-9]+/)
    .filter(Boolean)
    .map((part) => part[0].toUpperCase() + part.slice(1))
    .join("");
}

async function exists(path) {
  try {
    await access(path);
    return true;
  } catch {
    return false;
  }
}

const slug = option("name") ?? positionalName();
if (!slug || !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug)) {
  throw new Error("Pass a kebab-case scene name, for example: ./animation svg new buffer-cache");
}

const sceneName = pascalCase(slug);
const scriptDirectory = dirname(fileURLToPath(import.meta.url));
const templateDirectory = resolve(scriptDirectory, "../templates/new-scene");
const destinationDirectory = resolve("src/scenes", slug);
const replacements = new Map([
  ["__SLUG__", slug],
  ["__SCENE__", sceneName],
]);
const files = [
  ["model.ts.template", "model.ts"],
  ["Animation.tsx.template", `${sceneName}Animation.tsx`],
  ["README.md.template", "README.md"],
];

for (const [, destinationName] of files) {
  const destination = resolve(destinationDirectory, destinationName);
  if (await exists(destination)) throw new Error(`Refusing to overwrite ${destination}`);
}

for (const [templateName, destinationName] of files) {
  let contents = await readFile(resolve(templateDirectory, templateName), "utf8");
  for (const [from, to] of replacements) contents = contents.replaceAll(from, to);
  const destination = resolve(destinationDirectory, destinationName);
  await mkdir(dirname(destination), { recursive: true });
  await writeFile(destination, contents);
  process.stdout.write(`created ${destination}\n`);
}

process.stdout.write(`
Register in src/scenes/index.tsx:

import { ${sceneName}Animation } from "./${slug}/${sceneName}Animation";
import {
  getCheckpoints as get${sceneName}Checkpoints,
  getDurationMs as get${sceneName}DurationMs,
  get${sceneName}State,
  inspect${sceneName}State,
  validate${sceneName},
} from "./${slug}/model";

const ${sceneName[0].toLowerCase()}${sceneName.slice(1)}: SceneDefinition = {
  id: "${slug}",
  title: "${slug.replaceAll("-", " ")}",
  width: 1280,
  height: 720,
  profiles: ["fast", "presenter"],
  durationMs: get${sceneName}DurationMs,
  checkpoints: get${sceneName}Checkpoints,
  inspect: inspect${sceneName}State,
  validate: validate${sceneName},
  render: (timeMs, profile) => (
    <${sceneName}Animation state={get${sceneName}State(timeMs, profile)} />
  ),
};

Then add ${sceneName[0].toLowerCase()}${sceneName.slice(1)} to the exported scenes array and run ./animation svg check.
`);
