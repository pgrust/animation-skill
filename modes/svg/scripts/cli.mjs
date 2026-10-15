export function option(name, fallback) {
  const index = process.argv.indexOf(`--${name}`);
  return index >= 0 ? process.argv[index + 1] : fallback;
}

export function numberOption(name, fallback) {
  const value = Number(option(name, String(fallback)));
  if (!Number.isFinite(value)) throw new Error(`--${name} must be a number`);
  return value;
}

export function positiveIntegerOption(name, fallback) {
  const value = numberOption(name, fallback);
  if (!Number.isInteger(value) || value <= 0) {
    throw new Error(`--${name} must be a positive integer`);
  }
  return value;
}
