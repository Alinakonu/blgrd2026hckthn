"use client";

import type { AnalyzeResult } from "@/lib/types";

function ScoreBar({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <div className="mb-1 flex justify-between text-xs uppercase tracking-wide text-[var(--muted)]">
        <span>{label}</span>
        <span>{value}</span>
      </div>
      <div className="h-1.5 w-full overflow-hidden bg-[var(--rule)]">
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
    <div className="space-y-4 animate-rise">
      <div className="flex flex-wrap items-end justify-between gap-2">
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-[var(--muted)]">
            Climate stress · {result.horizon}
          </p>
          <p className="font-[family-name:var(--font-display)] text-3xl text-[var(--ink)]">
            {stress.overallScore}
            <span className="ml-2 text-base text-[var(--muted)]">/ 100</span>
          </p>
        </div>
        <p className="text-xs text-[var(--muted)]">
          {mode === "fixture" ? "Fixture data" : "Live APIs"}
          {parcelName ? ` · ${parcelName}` : ""}
        </p>
      </div>

      <div className="grid gap-3 sm:grid-cols-3">
        <ScoreBar label="Heat" value={stress.heatScore} />
        <ScoreBar label="Drought" value={stress.droughtScore} />
        <ScoreBar label="Extreme precip" value={stress.extremePrecipScore} />
      </div>

      <dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm sm:grid-cols-4">
        <div>
          <dt className="text-[var(--muted)]">Δ temp</dt>
          <dd className="text-[var(--ink)]">+{stress.heatDeltaC}°C</dd>
        </div>
        <div>
          <dt className="text-[var(--muted)]">Δ precip</dt>
          <dd className="text-[var(--ink)]">{stress.precipChangePct}%</dd>
        </div>
        <div>
          <dt className="text-[var(--muted)]">Soil pH</dt>
          <dd className="text-[var(--ink)]">{soil.ph?.toFixed(1) ?? "—"}</dd>
        </div>
        <div>
          <dt className="text-[var(--muted)]">SOC</dt>
          <dd className="text-[var(--ink)]">
            {soil.socGPerKg != null ? `${soil.socGPerKg.toFixed(1)} g/kg` : "—"}
          </dd>
        </div>
        <div className="col-span-2 sm:col-span-4">
          <dt className="text-[var(--muted)]">Texture</dt>
          <dd className="text-[var(--ink)]">{soil.textureLabel}</dd>
        </div>
      </dl>
    </div>
  );
}
