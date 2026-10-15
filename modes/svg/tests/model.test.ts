import assert from "node:assert/strict";
import test from "node:test";
import {
  getCheckpoints,
  getDurationMs,
  getPipelineState,
  TASKS,
  validatePipeline,
} from "../src/scenes/task-pipeline/model.ts";
import type { DeliveryProfile } from "../src/runtime/scene.ts";

const profiles: DeliveryProfile[] = ["fast", "presenter"];

test("both profiles preserve the same final task identities", () => {
  assert.equal(getDurationMs("fast"), 6_040);
  assert.equal(getDurationMs("presenter"), 11_200);

  for (const profile of profiles) {
    const state = getPipelineState(getDurationMs(profile), profile);
    assert.deepEqual(
      state.tasks.map((task) => [task.id, task.phase]),
      TASKS.map((task) => [task.id, "committed"]),
    );
    assert.deepEqual(state.counts, { queued: 0, inFlight: 0, committed: 6 });
  }
});

test("every sampled time partitions each task into one owner", () => {
  for (const profile of profiles) {
    let lastCommitted = 0;
    for (let timeMs = 0; timeMs <= getDurationMs(profile); timeMs += 17) {
      const state = getPipelineState(timeMs, profile);
      assert.equal(
        state.counts.queued + state.counts.inFlight + state.counts.committed,
        TASKS.length,
      );
      assert.equal(new Set(state.tasks.map((task) => task.id)).size, TASKS.length);
      assert.ok(state.counts.committed >= lastCommitted);
      lastCommitted = state.counts.committed;
    }
    assert.deepEqual(validatePipeline(profile), []);
  }
});

test("checkpoints stay ordered and inside each profile", () => {
  for (const profile of profiles) {
    const durationMs = getDurationMs(profile);
    const checkpoints = getCheckpoints(profile);
    assert.deepEqual(
      checkpoints.map((checkpoint) => checkpoint.id),
      ["orientation", "peak-motion", "first-commit", "final"],
    );
    assert.ok(checkpoints.every((checkpoint) => checkpoint.timeMs >= 0));
    assert.ok(checkpoints.every((checkpoint) => checkpoint.timeMs <= durationMs));
    assert.deepEqual(
      [...checkpoints].sort((left, right) => left.timeMs - right.timeMs),
      checkpoints,
    );
  }
});
