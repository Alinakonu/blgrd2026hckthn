"use client";

import type { AdaptationAction } from "@/lib/types";

export default function AdaptationChecklist({ actions }: { actions: AdaptationAction[] }) {
  return (
    <ol className="space-y-3">
      {actions.map((action) => (
        <li
          key={action.id}
          className="border-l-2 border-[var(--accent)] pl-4 py-1 animate-rise"
          style={{ animationDelay: `${action.rank * 60}ms` }}
        >
          <div className="flex flex-wrap items-baseline gap-2">
            <span className="font-[family-name:var(--font-display)] text-lg text-[var(--ink)]">
              {action.rank}. {action.title}
            </span>
            <span
              className={`text-[10px] uppercase tracking-wider ${
                action.priority === "high"
                  ? "text-[var(--danger)]"
                  : action.priority === "medium"
                    ? "text-[var(--warn)]"
                    : "text-[var(--muted)]"
              }`}
            >
              {action.priority}
            </span>
          </div>
          <p className="mt-1 text-sm text-[var(--ink-soft)]">{action.why}</p>
          <p className="mt-1 text-sm text-[var(--muted)]">
            <span className="text-[var(--ink)]">How: </span>
            {action.how}
          </p>
          <p className="mt-2 text-xs text-[var(--muted)]">
            Sources:{" "}
            {action.cites.map((c, i) => (
              <span key={c.url}>
                {i > 0 ? " · " : ""}
                <a
                  href={c.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="underline decoration-[var(--accent)] underline-offset-2 hover:text-[var(--ink)]"
                >
                  {c.label}
                </a>
              </span>
            ))}
          </p>
        </li>
      ))}
    </ol>
  );
}
