import { useCallback, useEffect, useRef, useState } from "react";
import { FeedbackOverlay } from "./FeedbackOverlay";
import { isDeliveryProfile, type DeliveryProfile, type SceneDefinition } from "./runtime/scene";
import { findScene, scenes } from "./scenes";

const params = new URLSearchParams(window.location.search);
const requestedSceneId = params.get("scene") ?? scenes[0].id;
function requireScene(id: string): SceneDefinition {
  const match = findScene(id);
  if (!match) throw new Error(`Unknown scene: ${id}`);
  return match;
}

function requireProfile(value: string, targetScene: SceneDefinition): DeliveryProfile {
  if (!isDeliveryProfile(value) || !targetScene.profiles.includes(value)) {
    throw new Error(`Unsupported profile for ${targetScene.id}: ${value}`);
  }
  return value;
}

const scene = requireScene(requestedSceneId);
const requestedProfile = requireProfile(params.get("profile") ?? "fast", scene);

const exportMode = params.get("export") === "1";
const feedbackMode = params.get("feedback") === "1";
const durationMs = scene.durationMs(requestedProfile);
const requestedTimeMs = params.has("t") ? Number(params.get("t")) : undefined;
const initialTimeMs = requestedTimeMs === undefined
  ? undefined
  : Number.isFinite(requestedTimeMs)
    ? Math.min(durationMs, Math.max(0, requestedTimeMs))
    : 0;
const autoplay = !exportMode
  && initialTimeMs === undefined
  && params.get("autoplay") !== "0";

export function App() {
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const [timeMs, setTimeMs] = useState(initialTimeMs ?? (reducedMotion ? durationMs : 0));
  const [playing, setPlaying] = useState(autoplay && !reducedMotion);
  const currentTime = useRef(timeMs);
  const startedAt = useRef(performance.now() - timeMs);

  const seek = useCallback((value: number) => {
    const next = Math.min(durationMs, Math.max(0, value));
    currentTime.current = next;
    startedAt.current = performance.now() - next;
    setTimeMs(next);
  }, []);

  useEffect(() => {
    currentTime.current = timeMs;
  }, [timeMs]);

  useEffect(() => {
    if (!playing) return;
    let frame = 0;
    const tick = (now: number) => {
      const next = (now - startedAt.current) % durationMs;
      currentTime.current = next;
      setTimeMs(next);
      frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [playing]);

  useEffect(() => {
    window.__CODE_ANIMATION__ = {
      sceneId: scene.id,
      profile: requestedProfile,
      width: scene.width,
      height: scene.height,
      durationMs,
      checkpoints: scene.checkpoints(requestedProfile),
      getTime: () => currentTime.current,
      setTime: (nextTimeMs) => {
        setPlaying(false);
        seek(nextTimeMs);
      },
      play: () => {
        startedAt.current = performance.now() - currentTime.current;
        setPlaying(true);
      },
      pause: () => setPlaying(false),
      inspect: (inspectionTimeMs = currentTime.current) =>
        scene.inspect(inspectionTimeMs, requestedProfile),
      validate: () => scene.validate(requestedProfile),
    };
  }, [seek]);

  const togglePlayback = () => {
    if (!playing) startedAt.current = performance.now() - currentTime.current;
    setPlaying((value) => !value);
  };

  return (
    <main className={`app${exportMode ? " export" : ""}${feedbackMode ? " feedback" : ""}`}>
      <section
        className="animation-frame"
        style={{ aspectRatio: `${scene.width} / ${scene.height}` }}
        onClick={exportMode || feedbackMode ? undefined : togglePlayback}
      >
        {scene.render(timeMs, requestedProfile)}
        {feedbackMode && (
          <FeedbackOverlay
            sceneId={scene.id}
            profile={requestedProfile}
            sceneWidth={scene.width}
            sceneHeight={scene.height}
          />
        )}
      </section>
      {!exportMode && (
        <section className="controls" aria-label="Animation controls">
          <button type="button" onClick={togglePlayback}>{playing ? "Pause" : "Play"}</button>
          <input
            type="range"
            min="0"
            max={durationMs}
            step="16"
            value={timeMs}
            onChange={(event) => {
              setPlaying(false);
              seek(Number(event.target.value));
            }}
            aria-label="Animation time"
          />
          <output>{(timeMs / 1000).toFixed(1)}s</output>
          <nav aria-label="Delivery profile">
            {scene.profiles.map((profile) => (
              <a
                key={profile}
                href={`?scene=${scene.id}&profile=${profile}${feedbackMode ? "&autoplay=0&feedback=1" : ""}`}
                aria-current={profile === requestedProfile ? "page" : undefined}
              >
                {profile}
              </a>
            ))}
          </nav>
        </section>
      )}
    </main>
  );
}
