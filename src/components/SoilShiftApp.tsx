"use client";

import { useEffect, useRef, useState, useTransition } from "react";
import FieldMapClient from "@/components/FieldMapClient";
import AdaptationChecklist from "@/components/AdaptationChecklist";
import StressPanel from "@/components/StressPanel";
import LinkedInIntelStub from "@/components/LinkedInIntelStub";
import { CROPS, DEMO_PARCELS } from "@/lib/parcels";
import type {
  AnalyzeResult,
  CropId,
  HorizonId,
  SoilTelemetry,
} from "@/lib/types";

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
  const [horizonKey, setHorizonKey] = useState(0);
  const planRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    setHorizonKey((n) => n + 1);
  }, [horizon]);

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
            parcelId: parcelId || undefined,
            telemetry: Object.fromEntries(
              Object.entries(telemetry).filter(
                ([, v]) => v != null && !Number.isNaN(v),
              ),
            ),
          }),
        });
        const json = await res.json();
        if (!res.ok) throw new Error(json.error ?? "Analyze failed");
        setResult(json as AnalyzeResult);
        requestAnimationFrame(() => {
          planRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
        });
      } catch (err) {
        setResult(null);
        setError(err instanceof Error ? err.message : "Analyze failed");
      }
    });
  }

  return (
    <div className="relative min-h-screen">
      <header className="relative flex min-h-[100svh] flex-col justify-end overflow-hidden px-4 pb-14 pt-8 sm:px-8 sm:pb-20">
        <div className="pointer-events-none absolute inset-0" aria-hidden>
          <div className="absolute -left-20 top-8 h-80 w-80 rounded-full bg-[rgba(168,196,176,0.55)] blur-3xl" />
          <div className="absolute right-[-3rem] top-16 h-72 w-72 rounded-full bg-[rgba(214,226,216,0.7)] blur-3xl" />
          <div className="absolute bottom-0 left-0 right-0 h-40 bg-gradient-to-t from-[var(--bg)] to-transparent" />
        </div>

        <nav className="relative mb-auto flex items-center justify-between animate-hero">
          <span className="text-[11px] uppercase tracking-[0.22em] text-[var(--muted)]">
            AgriSense · field notes
          </span>
          <a
            href="#locate"
            className="text-[11px] uppercase tracking-[0.18em] text-[var(--ink-soft)] transition hover:text-[var(--accent)]"
          >
            Locate field ↓
          </a>
        </nav>

        <div className="relative mx-auto w-full max-w-6xl">
          <p
            className="animate-hero font-[family-name:var(--font-display)] text-[clamp(4.25rem,16vw,9.5rem)] leading-[0.86] tracking-[-0.04em] text-[var(--ink)]"
            style={{ animationDelay: "80ms" }}
          >
            Soil
            <span className="text-[var(--accent)]">Shift</span>
          </p>
          <div
            className="mt-8 flex max-w-xl flex-col gap-5 animate-hero"
            style={{ animationDelay: "180ms" }}
          >
            <h1 className="text-lg font-medium leading-snug text-[var(--ink)] sm:text-xl">
              Pin a field. Pick a crop. Get soil adaptations for the 2030s and 2050s.
            </h1>
            <p className="text-sm leading-relaxed text-[var(--ink-soft)] sm:text-base">
              Not a weather forecast — a calm, ranked checklist for how this soil
              should change before climate stress hits yields.
            </p>
            <div className="flex flex-wrap gap-3 pt-1">
              <button
                type="button"
                onClick={runAnalyze}
                disabled={pending}
                className="btn-primary px-6 py-3 text-sm disabled:opacity-60"
              >
                {pending ? "Reading the field…" : "Run adaptation plan"}
              </button>
              <a href="#locate" className="btn-ghost px-6 py-3 text-sm">
                Start with the map
              </a>
            </div>
          </div>
        </div>
      </header>

      <main className="relative mx-auto w-full max-w-6xl space-y-24 px-4 pb-24 sm:px-8">
        <section id="locate" className="scroll-mt-8 space-y-8">
          <div className="max-w-xl space-y-3 animate-rise">
            <p className="text-[11px] uppercase tracking-[0.22em] text-[var(--muted)]">
              01 — Locate
            </p>
            <h2 className="font-[family-name:var(--font-display)] text-4xl tracking-tight text-[var(--ink)] sm:text-5xl">
              Drop a pin on the field
            </h2>
            <p className="text-sm leading-relaxed text-[var(--ink-soft)]">
              Click the map or load a Vojvodina demo parcel. Optional AgriSense
              telemetry sharpens the advice.
            </p>
          </div>

          <div
            className="map-frame h-[min(62vh,32rem)] w-full animate-rise"
            style={{ animationDelay: "100ms" }}
          >
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
                className={`chip px-3 py-1.5 text-xs ${
                  parcelId === p.id ? "chip-active" : ""
                }`}
              >
                {p.name}
              </button>
            ))}
          </div>

          <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              <label className="text-[11px] uppercase tracking-[0.14em] text-[var(--muted)]">
                Lat
                <input
                  className="field-input"
                  type="number"
                  step="0.0001"
                  value={lat}
                  onChange={(e) => setLat(Number(e.target.value))}
                />
              </label>
              <label className="text-[11px] uppercase tracking-[0.14em] text-[var(--muted)]">
                Lon
                <input
                  className="field-input"
                  type="number"
                  step="0.0001"
                  value={lon}
                  onChange={(e) => setLon(Number(e.target.value))}
                />
              </label>
              <label className="text-[11px] uppercase tracking-[0.14em] text-[var(--muted)]">
                Crop
                <select
                  className="field-input"
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
              <div className="text-[11px] uppercase tracking-[0.14em] text-[var(--muted)]">
                Horizon
                <div className="horizon-track relative mt-1.5 grid grid-cols-2 p-1">
                  <span
                    key={horizonKey}
                    className="horizon-indicator pointer-events-none absolute bottom-1 top-1 w-[calc(50%-4px)] bg-[var(--accent)]"
                    style={{
                      left: horizon === "2030s" ? "4px" : "calc(50%)",
                    }}
                  />
                  {(["2030s", "2050s"] as HorizonId[]).map((h) => (
                    <button
                      key={h}
                      type="button"
                      onClick={() => setHorizon(h)}
                      className={`relative z-10 px-2 py-1.5 text-xs font-medium transition ${
                        horizon === h
                          ? "text-[var(--accent-ink)]"
                          : "text-[var(--ink-soft)] hover:text-[var(--ink)]"
                      }`}
                    >
                      {h}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <details className="soft-panel px-3 py-3">
                <summary className="cursor-pointer text-sm text-[var(--ink)]">
                  Optional AgriSense soil telemetry (NPK / pH / moisture)
                </summary>
                <div className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-3">
                  {(
                    [
                      ["n", "N"],
                      ["p", "P"],
                      ["k", "K"],
                      ["ph", "pH"],
                      ["moisture", "Moisture"],
                    ] as const
                  ).map(([key, label]) => (
                    <label
                      key={key}
                      className="text-[11px] uppercase tracking-[0.14em] text-[var(--muted)]"
                    >
                      {label}
                      <input
                        className="field-input"
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

              <div className="flex flex-wrap gap-3 pt-1">
                <button
                  type="button"
                  onClick={runAnalyze}
                  disabled={pending}
                  className="btn-primary px-5 py-2.5 text-sm disabled:opacity-60"
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
                    setError(null);
                  }}
                  className="btn-ghost px-5 py-2.5 text-sm"
                >
                  Reset demo
                </button>
              </div>
            </div>
          </div>
        </section>

        <section ref={planRef} id="plan" className="scroll-mt-8 space-y-8">
          <div className="max-w-xl space-y-3">
            <p className="text-[11px] uppercase tracking-[0.22em] text-[var(--muted)]">
              02 — Adapt
            </p>
            <h2 className="font-[family-name:var(--font-display)] text-4xl tracking-tight text-[var(--ink)] sm:text-5xl">
              Ranked soil shifts
            </h2>
            <p className="text-sm leading-relaxed text-[var(--ink-soft)]">
              Stress scores for this pin + crop, then the practices that matter most
              before the chosen horizon.
            </p>
          </div>

          {error && (
            <p className="border border-[var(--danger)] bg-[rgba(255,122,110,0.08)] px-4 py-3 text-sm text-[var(--danger)]">
              {error}
            </p>
          )}

          {!result && !error && (
            <p className="text-sm text-[var(--muted)]">
              Happy path: Novi Sad maize · 2050s · fixtures on → Run adaptation plan.
            </p>
          )}

          {result && (
            <div className="grid gap-12 lg:grid-cols-[0.9fr_1.1fr]">
              <StressPanel result={result} />
              <div>
                <h3 className="mb-4 text-[11px] uppercase tracking-[0.22em] text-[var(--muted)]">
                  Checklist
                </h3>
                <AdaptationChecklist actions={result.actions.slice(0, 6)} />
                <p className="mt-8 text-xs leading-relaxed text-[var(--muted)]">
                  {result.disclaimer}
                </p>
                <p className="mt-3 text-xs text-[var(--muted)]">
                  Data:{" "}
                  {result.credits.map((c, i) => (
                    <span key={c.key}>
                      {i > 0 ? " · " : ""}
                      <span dangerouslySetInnerHTML={{ __html: c.html }} />
                    </span>
                  ))}
                </p>
              </div>
            </div>
          )}

          <LinkedInIntelStub />
        </section>
      </main>

      <footer className="border-t border-[var(--rule)] px-4 py-8 text-center text-[11px] uppercase tracking-[0.18em] text-[var(--muted)]">
        SoilShift · Grok Bot Serbia Hackathon 2026
      </footer>
    </div>
  );
}
