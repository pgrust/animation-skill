import type { SceneDefinition } from "../runtime/scene";
import { TaskPipelineAnimation } from "./task-pipeline/TaskPipelineAnimation";
import {
  getCheckpoints,
  getDurationMs,
  getPipelineState,
  inspectPipelineState,
  validatePipeline,
} from "./task-pipeline/model";

const taskPipeline: SceneDefinition = {
  id: "task-pipeline",
  title: "Task pipeline",
  width: 1280,
  height: 720,
  profiles: ["fast", "presenter"],
  durationMs: getDurationMs,
  checkpoints: getCheckpoints,
  inspect: inspectPipelineState,
  validate: validatePipeline,
  render: (timeMs, profile) => (
    <TaskPipelineAnimation state={getPipelineState(timeMs, profile)} />
  ),
};

export const scenes = [taskPipeline] as const;

export function findScene(id: string): SceneDefinition | undefined {
  return scenes.find((scene) => scene.id === id);
}
