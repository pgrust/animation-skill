import type { Checkpoint, DeliveryProfile } from "../../runtime/scene";

export const TASKS = [
  { id: "J1", payload: "alpha" },
  { id: "J2", payload: "bravo" },
  { id: "J3", payload: "charlie" },
  { id: "J4", payload: "delta" },
  { id: "J5", payload: "echo" },
  { id: "J6", payload: "foxtrot" },
] as const;

export type TaskPhase =
  | "queued"
  | "to-check"
  | "checking"
  | "to-commit"
  | "committed";

export type TaskState = {
  id: string;
  payload: string;
  index: number;
  phase: TaskPhase;
  phaseProgress: number;
};

export type PipelineState = {
  timeMs: number;
  profile: DeliveryProfile;
  tasks: readonly TaskState[];
  counts: {
    queued: number;
    inFlight: number;
    committed: number;
  };
  completion: number;
};

type Timing = {
  introMs: number;
  staggerMs: number;
  toCheckMs: number;
  checkHoldMs: number;
  toCommitMs: number;
  finalHoldMs: number;
};

const TIMINGS: Record<DeliveryProfile, Timing> = {
  fast: {
    introMs: 500,
    staggerMs: 500,
    toCheckMs: 700,
    checkHoldMs: 240,
    toCommitMs: 700,
    finalHoldMs: 1_400,
  },
  presenter: {
    introMs: 1_000,
    staggerMs: 950,
    toCheckMs: 1_200,
    checkHoldMs: 650,
    toCommitMs: 1_200,
    finalHoldMs: 2_400,
  },
};

const clamp = (value: number, minimum = 0, maximum = 1) =>
  Math.min(maximum, Math.max(minimum, value));

export const mix = (from: number, to: number, progress: number) =>
  from + (to - from) * progress;

export function easeInOutCubic(value: number) {
  const progress = clamp(value);
  return progress < 0.5
    ? 4 * progress * progress * progress
    : 1 - Math.pow(-2 * progress + 2, 3) / 2;
}

function scheduleFor(index: number, profile: DeliveryProfile) {
  const timing = TIMINGS[profile];
  const start = timing.introMs + index * timing.staggerMs;
  const check = start + timing.toCheckMs;
  const commit = check + timing.checkHoldMs;
  const done = commit + timing.toCommitMs;
  return { start, check, commit, done };
}

export function getDurationMs(profile: DeliveryProfile) {
  const last = scheduleFor(TASKS.length - 1, profile);
  return last.done + TIMINGS[profile].finalHoldMs;
}

function getTaskState(
  timeMs: number,
  index: number,
  profile: DeliveryProfile,
): TaskState {
  const task = TASKS[index];
  const timing = TIMINGS[profile];
  const schedule = scheduleFor(index, profile);

  if (timeMs < schedule.start) {
    return { ...task, index, phase: "queued", phaseProgress: 0 };
  }
  if (timeMs < schedule.check) {
    return {
      ...task,
      index,
      phase: "to-check",
      phaseProgress: clamp((timeMs - schedule.start) / timing.toCheckMs),
    };
  }
  if (timeMs < schedule.commit) {
    return {
      ...task,
      index,
      phase: "checking",
      phaseProgress: clamp((timeMs - schedule.check) / timing.checkHoldMs),
    };
  }
  if (timeMs < schedule.done) {
    return {
      ...task,
      index,
      phase: "to-commit",
      phaseProgress: clamp((timeMs - schedule.commit) / timing.toCommitMs),
    };
  }
  return { ...task, index, phase: "committed", phaseProgress: 1 };
}

export function getPipelineState(
  inputTimeMs: number,
  profile: DeliveryProfile,
): PipelineState {
  const timeMs = clamp(inputTimeMs, 0, getDurationMs(profile));
  const tasks = TASKS.map((_, index) => getTaskState(timeMs, index, profile));
  const queued = tasks.filter((task) => task.phase === "queued").length;
  const committed = tasks.filter((task) => task.phase === "committed").length;
  const inFlight = tasks.length - queued - committed;

  return {
    timeMs,
    profile,
    tasks,
    counts: { queued, inFlight, committed },
    completion: committed / TASKS.length,
  };
}

export function getCheckpoints(profile: DeliveryProfile): readonly Checkpoint[] {
  const first = scheduleFor(0, profile);
  const third = scheduleFor(2, profile);
  const durationMs = getDurationMs(profile);
  return [
    { id: "orientation", label: "All jobs queued", timeMs: Math.min(300, first.start / 2) },
    {
      id: "peak-motion",
      label: "Overlapping jobs keep distinct owners",
      timeMs: third.start + TIMINGS[profile].toCheckMs / 2,
    },
    { id: "first-commit", label: "First job committed", timeMs: first.done + 40 },
    { id: "final", label: "All jobs committed", timeMs: durationMs - 120 },
  ];
}

export function inspectPipelineState(
  timeMs: number,
  profile: DeliveryProfile,
): Record<string, unknown> {
  const state = getPipelineState(timeMs, profile);
  return {
    timeMs: state.timeMs,
    profile: state.profile,
    counts: state.counts,
    completion: state.completion,
    tasks: state.tasks.map((task) => ({
      id: task.id,
      payload: task.payload,
      phase: task.phase,
    })),
  };
}

export function validatePipeline(profile: DeliveryProfile): readonly string[] {
  const errors: string[] = [];
  const durationMs = getDurationMs(profile);
  let lastCommitted = 0;

  for (let timeMs = 0; timeMs <= durationMs; timeMs += 25) {
    const state = getPipelineState(timeMs, profile);
    const ids = new Set(state.tasks.map((task) => task.id));
    const countTotal = state.counts.queued + state.counts.inFlight + state.counts.committed;
    if (ids.size !== TASKS.length) errors.push(`Duplicate task identity at ${timeMs} ms`);
    if (countTotal !== TASKS.length) errors.push(`Count partition failed at ${timeMs} ms`);
    if (state.counts.committed < lastCommitted) {
      errors.push(`Committed count moved backward at ${timeMs} ms`);
    }
    lastCommitted = state.counts.committed;
  }

  const finalState = getPipelineState(durationMs, profile);
  const finalIds = finalState.tasks
    .filter((task) => task.phase === "committed")
    .map((task) => task.id);
  if (finalIds.join(",") !== TASKS.map((task) => task.id).join(",")) {
    errors.push("Final committed identities do not match the source event table");
  }
  return errors;
}
