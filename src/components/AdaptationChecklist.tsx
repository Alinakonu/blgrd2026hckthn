"use client";

import type { AdaptationAction } from "@/lib/types";

export default function AdaptationChecklist({
  actions,
}: {
  actions: AdaptationAction[];
}) {
  return (
    <ol className="space-y-0">
      {actions.map((action) => (
        <li
          key={action.id}
          className="group border-t border-[var(--rule)] py-5 animate-rise first:border-t-0 first:pt-0"
          style={{ animationDelay: `${action.rank * 70}ms` }}
        >
          <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
            <span className="font-[family-name:var(--font-display)] text-2xl tracking-tight text-[var(--accent)]">
              {String(action.rank).padStart(2, "0")}
            </span>
            <span className="font-[family-name:var(--font-display)] text-xl tracking-tight text-[var(--ink)] transition group-hover:text-[var(--accent)]">
              {action.title}
            </span>
            <span
              className={`text-[10px] uppercase tracking-[0.18em] ${
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
          <p className="mt-2 max-w-2xl text-sm leading-relaxed text-[var(--ink-soft)]">
            {action.why}
          </p>
          <p className="mt-1.5 max-w-2xl text-sm leading-relaxed text-[var(--muted)]">
            <span className="text-[var(--ink)]">How — </span>
            {action.how}
          </p>
          <p className="mt-3 text-xs text-[var(--muted)]">
            Sources:{" "}
            {action.cites.map((c, i) => (
              <span key={c.url}>
                {i > 0 ? " · " : ""}
                <a
                  href={c.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="underline decoration-[var(--accent)]/50 underline-offset-2 transition hover:text-[var(--accent)] hover:decoration-[var(--accent)]"
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
