"use client";

import { useState, useTransition } from "react";
import FieldMapClient from "@/components/FieldMapClient";
import AdaptationChecklist from "@/components/AdaptationChecklist";
import StressPanel from "@/components/StressPanel";
import LinkedInIntelStub from "@/components/LinkedInIntelStub";
import { CROPS, DEMO_PARCELS } from "@/lib/parcels";
import type { AnalyzeResult, CropId, HorizonId, SoilTelemetry } from "@/lib/types";

const DEFAULT = DEMO_PARCELS[0];

export default function SoilShiftApp() {
  const [lat, setLat] = useState(DEFAULT.lat);
  const [lon, setLon] = useState(DEFAULT.lon);
  const [crop, setCrop] = useState<CropId>(DEFAULT.defaultCrop);
  const [horizon, setHorizon] = useState<HorizonId>("2050s");
  const [parcelId, setParcelId] = useState<string>(DEFAULT.id);
  const [useFixture, setUseFixture] = useState(true);
  const [telemetry, setTelemetry] = useState<SoilTelemetry>({});
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pending, startTransition] = useTransition();

  function pickParcel(id: string) {
    const p = DEMO_PARCELS.find((x) => x.id === id);
    if (!p) return;
    setParcelId(p.id);
    setLat(p.lat);
    setLon(p.lon);
    setCrop(p.defaultCrop);
  }

  function runAnalyze() {
    setError(null);
    startTransition(async () => {
      try {
        const res = await fetch("/api/analyze", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            lat,
            lon,
            crop,
            horizon,
            useFixture,
            parcelId,
            telemetry: Object.fromEntries(
              Object.entries(telemetry).filter(([, v]) => v != null && !Number.isNaN(v)),
            ),
          }),
        });
        const json = await res.json();
        if (!res.ok) throw new Error(json.error ?? "Analyze failed");
        setResult(json as AnalyzeResult);
      } catch (err) {
        setResult(null);
        setError(err instanceof Error ? err.message : "Analyze failed");
      }
    });
  }

  return (
    <div className="min-h-screen">
      <header className="relative overflow-hidden border-b border-[var(--rule)]">
        <div className="hero-wash absolute inset-0" aria-hidden />
        <div className="relative mx-auto flex max-w-6xl flex-col gap-6 px-4 py-10 sm:px-6 sm:py-14">
          <p className="font-[family-name:var(--font-display)] text-5xl leading-none tracking-tight text-[var(--ink)] sm:text-6xl">
            SoilShift
          </p>
          <div className="max-w-xl space-y-3">
            <h1 className="text-lg font-medium text-[var(--ink)] sm:text-xl">
              Field + crop → soil adaptation for the 2030s and 2050s
            </h1>
            <p className="text-sm leading-relaxed text-[var(--ink-soft)]">
              Pin a parcel, optionally add AgriSense-style soil telemetry, and get a
              ranked checklist for how this soil should change before climate stress
              hits yields — not a weather forecast.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              onClick={runAnalyze}
              disabled={pending}
              className="bg-[var(--accent)] px-5 py-2.5 text-sm font-medium text-[var(--accent-ink)] transition hover:brightness-110 disabled:opacity-60"
            >
              {pending ? "Analyzing…" : "Run adaptation plan"}
            </button>
            <button
              type="button"
              onClick={() => {
                pickParcel(DEFAULT.id);
                setHorizon("2050s");
                setUseFixture(true);
                setTelemetry({});
                setResult(null);
              }}
              className="border border-[var(--rule-strong)] px-5 py-2.5 text-sm text-[var(--ink)] transition hover:bg-[var(--panel-muted)]"
            >
              Reset demo
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto grid max-w-6xl gap-8 px-4 py-8 sm:px-6 lg:grid-cols-[1.05fr_0.95fr]">
        <section className="space-y-5">
          <div className="space-y-2">
            <h2 className="font-[family-name:var(--font-display)] text-2xl text-[var(--ink)]">
              Locate field
            </h2>
            <p className="text-sm text-[var(--muted)]">
              Click the map or load a Vojvodina demo parcel.
            </p>
          </div>

          <div className="h-72 overflow-hidden border border-[var(--rule)] sm:h-80">
            <FieldMapClient
              lat={lat}
              lon={lon}
              onPick={(nextLat, nextLon) => {
                setLat(Number(nextLat.toFixed(5)));
                setLon(Number(nextLon.toFixed(5)));
                setParcelId("");
              }}
            />
          </div>

          <div className="flex flex-wrap gap-2">
            {DEMO_PARCELS.map((p) => (
              <button
                key={p.id}
                type="button"
                onClick={() => pickParcel(p.id)}
                className={`px-3 py-1.5 text-xs transition ${
                  parcelId === p.id
                    ? "bg-[var(--ink)] text-[var(--bg)]"
                    : "border border-[var(--rule-strong)] text-[var(--ink-soft)] hover:bg-[var(--panel-muted)]"
                }`}
              >
                {p.name}
              </button>
            ))}
          </div>

          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <label className="text-xs text-[var(--muted)]">
              Lat
              <input
                className="mt-1 w-full border border-[var(--rule)] bg-[var(--panel)] px-2 py-1.5 text-sm text-[var(--ink)]"
                type="number"
                step="0.0001"
                value={lat}
                onChange={(e) => setLat(Number(e.target.value))}
              />
            </label>
            <label className="text-xs text-[var(--muted)]">
              Lon
              <input
                className="mt-1 w-full border border-[var(--rule)] bg-[var(--panel)] px-2 py-1.5 text-sm text-[var(--ink)]"
                type="number"
                step="0.0001"
                value={lon}
                onChange={(e) => setLon(Number(e.target.value))}
              />
            </label>
            <label className="text-xs text-[var(--muted)]">
              Crop
              <select
                className="mt-1 w-full border border-[var(--rule)] bg-[var(--panel)] px-2 py-1.5 text-sm text-[var(--ink)]"
                value={crop}
                onChange={(e) => setCrop(e.target.value as CropId)}
              >
                {CROPS.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.label}
                  </option>
                ))}
              </select>
            </label>
            <label className="text-xs text-[var(--muted)]">
              Horizon
              <select
                className="mt-1 w-full border border-[var(--rule)] bg-[var(--panel)] px-2 py-1.5 text-sm text-[var(--ink)]"
                value={horizon}
                onChange={(e) => setHorizon(e.target.value as HorizonId)}
              >
                <option value="2030s">2030s</option>
                <option value="2050s">2050s</option>
              </select>
            </label>
          </div>

          <details className="border border-[var(--rule)] bg-[var(--panel-muted)] p-3">
            <summary className="cursor-pointer text-sm text-[var(--ink)]">
              Optional AgriSense soil telemetry (NPK / pH / moisture)
            </summary>
            <div className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-5">
              {(
                [
                  ["n", "N"],
                  ["p", "P"],
                  ["k", "K"],
                  ["ph", "pH"],
                  ["moisture", "Moisture"],
                ] as const
              ).map(([key, label]) => (
                <label key={key} className="text-xs text-[var(--muted)]">
                  {label}
                  <input
                    className="mt-1 w-full border border-[var(--rule)] bg-[var(--panel)] px-2 py-1.5 text-sm text-[var(--ink)]"
                    type="number"
                    step="0.1"
                    placeholder="—"
                    value={telemetry[key] ?? ""}
                    onChange={(e) => {
                      const v = e.target.value;
                      setTelemetry((t) => ({
                        ...t,
                        [key]: v === "" ? undefined : Number(v),
                      }));
                    }}
                  />
                </label>
              ))}
            </div>
          </details>

          <label className="flex items-center gap-2 text-sm text-[var(--ink-soft)]">
            <input
              type="checkbox"
              checked={useFixture}
              onChange={(e) => setUseFixture(e.target.checked)}
            />
            Use cached demo fixtures (recommended for live pitch)
          </label>
        </section>

        <section className="space-y-6">
          <div className="space-y-2">
            <h2 className="font-[family-name:var(--font-display)] text-2xl text-[var(--ink)]">
              Adaptation plan
            </h2>
            <p className="text-sm text-[var(--muted)]">
              Ranked soil practices tied to projected stress for this field and crop.
            </p>
          </div>

          {error && (
            <p className="border border-[var(--danger)] bg-[var(--danger-wash)] px-3 py-2 text-sm text-[var(--danger)]">
              {error}
            </p>
          )}

          {!result && !error && (
            <p className="text-sm text-[var(--muted)]">
              Run the plan to see drought/heat scores and top actions. Happy path:
              Novi Sad maize · 2050s · fixtures on.
            </p>
          )}

          {result && (
            <>
              <StressPanel result={result} />
              <div>
                <h3 className="mb-3 text-xs uppercase tracking-[0.18em] text-[var(--muted)]">
                  Ranked checklist
                </h3>
                <AdaptationChecklist actions={result.actions.slice(0, 6)} />
              </div>
              <p className="text-xs leading-relaxed text-[var(--muted)]">
                {result.disclaimer}
              </p>
              <p className="text-xs text-[var(--muted)]">
                Data:{" "}
                {result.credits.map((c, i) => (
                  <span key={c.key}>
                    {i > 0 ? " · " : ""}
                    <span dangerouslySetInnerHTML={{ __html: c.html }} />
                  </span>
                ))}
              </p>
            </>
          )}

          <LinkedInIntelStub />
        </section>
      </main>

      <footer className="border-t border-[var(--rule)] px-4 py-6 text-center text-xs text-[var(--muted)]">
        SoilShift · AgriSense soil loop + climate horizons · Grok Bot Serbia Hackathon 2026
      </footer>
    </div>
  );
}
