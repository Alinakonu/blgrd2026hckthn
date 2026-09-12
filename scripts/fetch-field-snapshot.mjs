#!/usr/bin/env node
/**
 * Daytona-friendly field snapshot script.
 *
 * Run inside a Daytona sandbox (or locally) to fetch SoilGrids + Open-Meteo
 * for a lat/lon and print JSON — useful for the Daytona prize track without
 * tying judges to the Next.js UI.
 *
 * Usage:
 *   node scripts/fetch-field-snapshot.mjs --lat 45.2671 --lon 19.8335 --horizon 2050s
 *   USE_FIXTURES=1 node scripts/fetch-field-snapshot.mjs
 */

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));

function arg(name, fallback) {
  const idx = process.argv.indexOf(`--${name}`);
  if (idx >= 0 && process.argv[idx + 1]) return process.argv[idx + 1];
  return fallback;
}

const lat = Number(arg("lat", "45.2671"));
const lon = Number(arg("lon", "19.8335"));
const horizon = arg("horizon", "2050s");
const useFixtures =
  process.env.USE_FIXTURES === "1" ||
  process.env.USE_FIXTURES === "true" ||
  process.argv.includes("--fixture");

async function fetchJson(url, ms = 12000) {
  const controller = new AbortController();
  const t = setTimeout(() => controller.abort(), ms);
  try {
    const res = await fetch(url, { signal: controller.signal });
    if (!res.ok) throw new Error(`${url} -> ${res.status}`);
    return await res.json();
  } finally {
    clearTimeout(t);
  }
}

async function liveSnapshot() {
  const soilParams = new URLSearchParams({
    lat: String(lat),
    lon: String(lon),
    depth: "0-5cm",
    value: "mean",
  });
  for (const p of ["phh2o", "soc", "clay", "sand", "silt"]) soilParams.append("property", p);

  const climateParams = new URLSearchParams({
    latitude: String(lat),
    longitude: String(lon),
    start_date: horizon === "2030s" ? "2030-01-01" : "2050-01-01",
    end_date: horizon === "2030s" ? "2039-12-31" : "2059-12-31",
    models: "EC_Earth3P_HR",
    daily: "temperature_2m_mean,precipitation_sum",
  });

  const [soil, climate] = await Promise.all([
    fetchJson(`https://rest.isric.org/soilgrids/v2.0/properties/query?${soilParams}`),
    fetchJson(`https://climate-api.open-meteo.com/v1/climate?${climateParams}`),
  ]);

  return { mode: "live", lat, lon, horizon, soil, climate };
}

function fixtureSnapshot() {
  const path = join(__dirname, "../src/data/fixtures/parcels.json");
  const data = JSON.parse(readFileSync(path, "utf8"));
  const parcel = data.parcels["vojvodina-maize"];
  return {
    mode: "fixture",
    lat,
    lon,
    horizon,
    soil: parcel.soil,
    baseline: parcel.baseline,
    projected: parcel.projected[horizon] ?? parcel.projected["2050s"],
  };
}

const result = useFixtures
  ? fixtureSnapshot()
  : await liveSnapshot().catch((err) => {
      console.error("Live fetch failed, falling back to fixtures:", err.message);
      return fixtureSnapshot();
    });

process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
