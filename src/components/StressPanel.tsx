"use client";

import type { AnalyzeResult } from "@/lib/types";

function ScoreBar({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <div className="mb-1.5 flex justify-between text-[11px] uppercase tracking-[0.16em] text-[var(--muted)]">
        <span>{label}</span>
        <span className="text-[var(--ink-soft)]">{value}</span>
      </div>
      <div className="h-[3px] w-full overflow-hidden bg-[var(--rule)]">
        <div
          className="h-full bg-[var(--accent)] transition-all duration-700 ease-out"
          style={{ width: `${Math.min(100, Math.max(0, value))}%` }}
        />
      </div>
    </div>
  );
}

export default function StressPanel({ result }: { result: AnalyzeResult }) {
  const { stress, soil, mode, parcelName } = result;
  return (
    <div className="space-y-5 animate-rise">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p className="text-[11px] uppercase tracking-[0.22em] text-[var(--muted)]">
            Climate stress · {result.horizon}
          </p>
          <p className="mt-1 font-[family-name:var(--font-display)] text-5xl leading-none tracking-tight text-[var(--ink)]">
            {stress.overallScore}
            <span className="ml-2 text-lg text-[var(--muted)]">/100</span>
          </p>
        </div>
        <p className="text-xs text-[var(--muted)]">
          {mode === "fixture" ? "Fixture data" : "Live APIs"}
          {parcelName ? ` · ${parcelName}` : ""}
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <ScoreBar label="Heat" value={stress.heatScore} />
        <ScoreBar label="Drought" value={stress.droughtScore} />
        <ScoreBar label="Extreme precip" value={stress.extremePrecipScore} />
      </div>

      <dl className="grid grid-cols-2 gap-x-6 gap-y-3 text-sm sm:grid-cols-4">
        <div>
          <dt className="text-[11px] uppercase tracking-[0.14em] text-[var(--muted)]">
            Δ temp
          </dt>
          <dd className="mt-0.5 text-[var(--ink)]">+{stress.heatDeltaC}°C</dd>
        </div>
        <div>
          <dt className="text-[11px] uppercase tracking-[0.14em] text-[var(--muted)]">
            Δ precip
          </dt>
          <dd className="mt-0.5 text-[var(--ink)]">{stress.precipChangePct}%</dd>
        </div>
        <div>
          <dt className="text-[11px] uppercase tracking-[0.14em] text-[var(--muted)]">
            Soil pH
          </dt>
          <dd className="mt-0.5 text-[var(--ink)]">{soil.ph?.toFixed(1) ?? "—"}</dd>
        </div>
        <div>
          <dt className="text-[11px] uppercase tracking-[0.14em] text-[var(--muted)]">
            SOC
          </dt>
          <dd className="mt-0.5 text-[var(--ink)]">
            {soil.socGPerKg != null ? `${soil.socGPerKg.toFixed(1)} g/kg` : "—"}
          </dd>
        </div>
        <div className="col-span-2 sm:col-span-4">
          <dt className="text-[11px] uppercase tracking-[0.14em] text-[var(--muted)]">
            Texture
          </dt>
          <dd className="mt-0.5 text-[var(--ink)]">{soil.textureLabel}</dd>
        </div>
      </dl>
    </div>
  );
}
