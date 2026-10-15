import type { Checkpoint, DeliveryProfile } from "./scene";

declare global {
  interface Window {
    __CODE_ANIMATION__: {
      sceneId: string;
      profile: DeliveryProfile;
      width: number;
      height: number;
      durationMs: number;
      checkpoints: readonly Checkpoint[];
      getTime: () => number;
      setTime: (timeMs: number) => void;
      play: () => void;
      pause: () => void;
      inspect: (timeMs?: number) => Record<string, unknown>;
      validate: () => readonly string[];
    };
  }
}

export {};
