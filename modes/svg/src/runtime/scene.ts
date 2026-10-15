import type { ReactNode } from "react";

export type DeliveryProfile = "fast" | "presenter";

export type Checkpoint = {
  id: string;
  label: string;
  timeMs: number;
};

export type SceneDefinition = {
  id: string;
  title: string;
  width: number;
  height: number;
  profiles: readonly DeliveryProfile[];
  durationMs: (profile: DeliveryProfile) => number;
  checkpoints: (profile: DeliveryProfile) => readonly Checkpoint[];
  inspect: (timeMs: number, profile: DeliveryProfile) => Record<string, unknown>;
  validate: (profile: DeliveryProfile) => readonly string[];
  render: (timeMs: number, profile: DeliveryProfile) => ReactNode;
};

export function isDeliveryProfile(value: string): value is DeliveryProfile {
  return value === "fast" || value === "presenter";
}
