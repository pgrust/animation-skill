import { useEffect, useRef, useState } from "react";
import type { DeliveryProfile } from "./runtime/scene";

export type FeedbackItem = {
  id: string;
  sceneId: string;
  profile: DeliveryProfile;
  timeMs: number;
  x: number;
  y: number;
  sceneWidth: number;
  sceneHeight: number;
  element: string;
  comment: string;
  status: "open" | "resolved";
  createdAt: string;
};

type FeedbackOverlayProps = {
  sceneId: string;
  profile: DeliveryProfile;
  sceneWidth: number;
  sceneHeight: number;
};

function describeElement(clientX: number, clientY: number) {
  const hit = document
    .elementsFromPoint(clientX, clientY)
    .find((node) => node instanceof SVGElement && node.tagName.toLowerCase() !== "svg");
  if (!(hit instanceof SVGElement)) return "stage background";

  const explicitId = hit.closest<SVGElement>("[data-feedback-id]")?.dataset.feedbackId;
  const parts: string[] = [];
  if (explicitId) parts.push(`id=${explicitId}`);
  if (hit instanceof SVGTextElement && hit.textContent?.trim()) {
    parts.push(`text ${JSON.stringify(hit.textContent.trim())}`);
  } else {
    const fill = hit.getAttribute("fill") ?? "none";
    const stroke = hit.getAttribute("stroke") ?? "none";
    parts.push(`<${hit.tagName.toLowerCase()}> fill=${fill} stroke=${stroke}`);
  }

  let group: Element | null = hit.parentElement;
  for (let depth = 0; depth < 3 && group?.tagName.toLowerCase() === "g"; depth += 1) {
    const labels = Array.from(group.querySelectorAll("text"))
      .map((node) => node.textContent?.trim())
      .filter((label): label is string => Boolean(label))
      .slice(0, 2);
    if (labels.length) {
      parts.push(`near ${labels.map((label) => JSON.stringify(label)).join(" / ")}`);
      break;
    }
    group = group.parentElement;
  }
  return parts.join(" ");
}

export function FeedbackOverlay({
  sceneId,
  profile,
  sceneWidth,
  sceneHeight,
}: FeedbackOverlayProps) {
  const [items, setItems] = useState<FeedbackItem[]>([]);
  const [draft, setDraft] = useState<FeedbackItem | null>(null);
  const [text, setText] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const layerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let cancelled = false;
    fetch("/__feedback")
      .then((response) => {
        if (!response.ok) throw new Error(`Feedback endpoint returned ${response.status}`);
        return response.json() as Promise<FeedbackItem[]>;
      })
      .then((all) => {
        if (!cancelled) {
          setItems(all.filter((item) => item.sceneId === sceneId && item.profile === profile));
        }
      })
      .catch((cause: unknown) => {
        if (!cancelled) setError(cause instanceof Error ? cause.message : "Could not load feedback");
      });
    return () => { cancelled = true; };
  }, [profile, sceneId]);

  const cancelDraft = () => {
    setDraft(null);
    setText("");
    setError("");
  };

  const onStageClick = (event: React.MouseEvent<HTMLDivElement>) => {
    if (draft) {
      cancelDraft();
      return;
    }
    const rect = layerRef.current?.getBoundingClientRect();
    if (!rect || rect.width <= 0 || rect.height <= 0) return;

    window.__CODE_ANIMATION__.pause();
    const x = Math.round(((event.clientX - rect.left) / rect.width) * sceneWidth);
    const y = Math.round(((event.clientY - rect.top) / rect.height) * sceneHeight);
    setDraft({
      id: crypto.randomUUID(),
      sceneId,
      profile,
      timeMs: Math.round(window.__CODE_ANIMATION__.getTime()),
      x: Math.min(sceneWidth, Math.max(0, x)),
      y: Math.min(sceneHeight, Math.max(0, y)),
      sceneWidth,
      sceneHeight,
      element: describeElement(event.clientX, event.clientY),
      comment: "",
      status: "open",
      createdAt: new Date().toISOString(),
    });
    setText("");
    setError("");
  };

  const save = async () => {
    if (!draft || !text.trim() || saving) return;
    const item = { ...draft, comment: text.trim() };
    setSaving(true);
    setError("");
    try {
      const response = await fetch("/__feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(item),
      });
      if (!response.ok) throw new Error(`Could not save note (${response.status})`);
      setItems((current) => [...current, item]);
      setDraft(null);
      setText("");
    } catch (cause: unknown) {
      setError(cause instanceof Error ? cause.message : "Could not save note");
    } finally {
      setSaving(false);
    }
  };

  const pinStyle = (item: Pick<FeedbackItem, "x" | "y">) => ({
    left: `${(item.x / sceneWidth) * 100}%`,
    top: `${(item.y / sceneHeight) * 100}%`,
  });
  const draftXPercent = draft ? (draft.x / sceneWidth) * 100 : 0;
  const draftYPercent = draft ? (draft.y / sceneHeight) * 100 : 0;

  return (
    <div ref={layerRef} className="feedback-layer" onClick={onStageClick}>
      <div className="feedback-badge" role="status">
        FEEDBACK MODE · click an element to leave a note · {items.length} saved
      </div>
      {items.map((item, index) => (
        <div
          key={item.id}
          className={`feedback-pin ${item.status}`}
          style={pinStyle(item)}
          title={`${item.element}: ${item.comment}`}
        >
          {index + 1}
        </div>
      ))}
      {draft && (
        <div className="feedback-pin draft" style={pinStyle(draft)}>{items.length + 1}</div>
      )}
      {draft && (
        <div
          className="feedback-form"
          style={{
            left: `${Math.min(98, Math.max(2, draftXPercent))}%`,
            top: `${Math.min(68, Math.max(8, draftYPercent + 3))}%`,
            transform: draftXPercent > 50 ? "translateX(-100%)" : undefined,
          }}
          onClick={(event) => event.stopPropagation()}
          role="dialog"
          aria-label="Leave animation feedback"
        >
          <div className="feedback-form-meta">
            t={(draft.timeMs / 1000).toFixed(2)}s · {draft.element}
          </div>
          <textarea
            autoFocus
            value={text}
            placeholder="What should change here?"
            aria-label="Feedback note"
            onChange={(event) => setText(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && (event.metaKey || event.ctrlKey)) void save();
              if (event.key === "Escape") cancelDraft();
            }}
          />
          {error && <div className="feedback-error" role="alert">{error}</div>}
          <div className="feedback-form-actions">
            <button type="button" onClick={cancelDraft}>Cancel</button>
            <button
              type="button"
              className="primary"
              disabled={!text.trim() || saving}
              onClick={() => void save()}
            >
              {saving ? "Saving…" : "Save note"}
            </button>
          </div>
        </div>
      )}
      {!draft && error && <div className="feedback-endpoint-error" role="alert">{error}</div>}
    </div>
  );
}
