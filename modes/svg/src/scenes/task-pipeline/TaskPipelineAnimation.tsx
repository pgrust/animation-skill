import {
  easeInOutCubic,
  mix,
  TASKS,
  type PipelineState,
  type TaskState,
} from "./model";

const COLORS = {
  background: "#0a0d12",
  surface: "#111722",
  surfaceRaised: "#17202c",
  border: "#2a3442",
  text: "#edf2f7",
  muted: "#8390a0",
  idle: "#526174",
  active: "#5ab4ff",
  committed: "#61d6a3",
};

const CARD = { width: 164, height: 36 };

function positionFor(task: TaskState) {
  const queue = { x: 132, y: 266 + task.index * 50 };
  const checker = { x: 556, y: 266 + task.index * 50 };
  const committed = { x: 976, y: 266 + task.index * 50 };
  const progress = easeInOutCubic(task.phaseProgress);

  if (task.phase === "to-check") {
    return { x: mix(queue.x, checker.x, progress), y: mix(queue.y, checker.y, progress) };
  }
  if (task.phase === "checking") return checker;
  if (task.phase === "to-commit") {
    return {
      x: mix(checker.x, committed.x, progress),
      y: mix(checker.y, committed.y, progress),
    };
  }
  return task.phase === "committed" ? committed : queue;
}

function TaskCard({ task }: { task: TaskState }) {
  const position = positionFor(task);
  const active = task.phase !== "queued" && task.phase !== "committed";
  const color = task.phase === "committed"
    ? COLORS.committed
    : active
      ? COLORS.active
      : COLORS.idle;

  return (
    <g
      transform={`translate(${position.x} ${position.y})`}
      filter={active ? "url(#active-glow)" : undefined}
    >
      <rect
        width={CARD.width}
        height={CARD.height}
        rx="9"
        fill={color}
        fillOpacity={active ? 0.2 : 0.11}
        stroke={color}
        strokeWidth={active ? 2 : 1.2}
      />
      <text x="16" y="24" className="job-id mono" fill={COLORS.text}>
        {task.id}
      </text>
      <text x="145" y="24" className="job-payload mono" fill={color} textAnchor="end">
        {task.payload}
      </text>
    </g>
  );
}

function Panel({
  x,
  title,
  detail,
  count,
  color,
}: {
  x: number;
  title: string;
  detail: string;
  count: number;
  color: string;
}) {
  return (
    <g>
      <rect x={x} y="190" width="292" height="414" rx="20" fill={COLORS.surface} stroke={COLORS.border} />
      <rect x={x} y="190" width="292" height="4" rx="2" fill={color} />
      <text x={x + 28} y="228" className="panel-title" fill={COLORS.text}>{title}</text>
      <text x={x + 28} y="250" className="panel-detail mono" fill={COLORS.muted}>{detail}</text>
      <text x={x + 264} y="235" className="panel-count mono" fill={color} textAnchor="end">{count}</text>
    </g>
  );
}

export function TaskPipelineAnimation({ state }: { state: PipelineState }) {
  const { counts } = state;
  return (
    <svg
      viewBox="0 0 1280 720"
      className="animation-stage"
      role="img"
      aria-label={`${counts.committed} of ${TASKS.length} jobs committed`}
    >
      <defs>
        <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
          <path d="M32 0H0V32" fill="none" stroke="#ffffff" strokeOpacity="0.025" />
        </pattern>
        <filter id="active-glow" x="-40%" y="-80%" width="180%" height="260%">
          <feGaussianBlur stdDeviation="8" result="blur" />
          <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
      </defs>

      <rect width="1280" height="720" fill={COLORS.background} />
      <rect width="1280" height="720" fill="url(#grid)" />
      <text x="64" y="72" className="headline" fill={COLORS.text}>ONE JOB, ONE OWNER</text>
      <text x="64" y="104" className="subtitle mono" fill={COLORS.muted}>
        QUEUE → CHECK → COMMIT · ILLUSTRATIVE TIMING
      </text>
      <text x="1216" y="84" className="profile mono" fill={COLORS.muted} textAnchor="end">
        {state.profile.toUpperCase()} PROFILE
      </text>

      <path d="M356 397H530" stroke={COLORS.border} strokeWidth="2" />
      <path d="M780 397H950" stroke={COLORS.border} strokeWidth="2" />
      <path d="M516 389L530 397L516 405" fill="none" stroke={COLORS.active} strokeWidth="2" />
      <path d="M936 389L950 397L936 405" fill="none" stroke={COLORS.committed} strokeWidth="2" />

      <Panel x={64} title="QUEUE" detail="WAITING" count={counts.queued} color={COLORS.idle} />
      <Panel x={494} title="CHECK" detail="IN FLIGHT" count={counts.inFlight} color={COLORS.active} />
      <Panel x={924} title="COMMIT" detail="SETTLED" count={counts.committed} color={COLORS.committed} />

      <g>{state.tasks.map((task) => <TaskCard key={task.id} task={task} />)}</g>

      <rect x="64" y="650" width="1152" height="8" rx="4" fill={COLORS.surfaceRaised} />
      <rect
        x="64"
        y="650"
        width={1152 * state.completion}
        height="8"
        rx="4"
        fill={COLORS.committed}
      />
      <text x="64" y="686" className="progress mono" fill={COLORS.muted}>COMMITTED</text>
      <text x="1216" y="686" className="progress mono" fill={COLORS.committed} textAnchor="end">
        {counts.committed} / {TASKS.length}
      </text>
    </svg>
  );
}
