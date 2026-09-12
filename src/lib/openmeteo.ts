import { fetchWithTimeout } from "./retryable";
import type { ClimateNormals, HorizonId } from "./types";

function yearRange(horizon: HorizonId): { start: string; end: string } {
  if (horizon === "2030s") {
    return { start: "2030-01-01", end: "2039-12-31" };
  }
  return { start: "2050-01-01", end: "2059-12-31" };
}

function summarizeDaily(temps: number[], precip: number[]): ClimateNormals {
  const meanTempC =
    temps.reduce((a, b) => a + b, 0) / Math.max(temps.length, 1);
  const years = Math.max(temps.length / 365, 1);
  const precipMmYear = precip.reduce((a, b) => a + b, 0) / years;
  const hotDaysApprox =
    temps.filter((t) => t >= 30).length / Math.max(years, 1);
  return {
    meanTempC: Number(meanTempC.toFixed(2)),
    precipMmYear: Number(precipMmYear.toFixed(0)),
    hotDaysApprox: Number(hotDaysApprox.toFixed(0)),
  };
}

/** Historical climate normals (~1991–2020 proxy via recent archive window). */
export async function fetchBaselineClimate(
  lat: number,
  lon: number,
): Promise<ClimateNormals> {
  const params = new URLSearchParams({
    latitude: String(lat),
    longitude: String(lon),
    start_date: "1991-01-01",
    end_date: "2020-12-31",
    daily: "temperature_2m_mean,precipitation_sum",
    timezone: "auto",
  });
  const url = `https://archive-api.open-meteo.com/v1/archive?${params}`;
  const res = await fetchWithTimeout(url, 15_000);
  if (!res.ok) throw new Error(`Open-Meteo archive HTTP ${res.status}`);
  const json = (await res.json()) as {
    daily?: { temperature_2m_mean?: (number | null)[]; precipitation_sum?: (number | null)[] };
  };
  const temps = (json.daily?.temperature_2m_mean ?? []).filter(
    (v): v is number => typeof v === "number",
  );
  const precip = (json.daily?.precipitation_sum ?? []).filter(
    (v): v is number => typeof v === "number",
  );
  if (!temps.length) throw new Error("Open-Meteo archive returned no temperatures");
  return summarizeDaily(temps, precip);
}

/** CMIP-style projected climate via Open-Meteo Climate API. */
export async function fetchProjectedClimate(
  lat: number,
  lon: number,
  horizon: HorizonId,
): Promise<ClimateNormals> {
  const { start, end } = yearRange(horizon);
  const params = new URLSearchParams({
    latitude: String(lat),
    longitude: String(lon),
    start_date: start,
    end_date: end,
    models: "EC_Earth3P_HR",
    daily: "temperature_2m_mean,precipitation_sum",
  });
  const url = `https://climate-api.open-meteo.com/v1/climate?${params}`;
  const res = await fetchWithTimeout(url, 15_000);
  if (!res.ok) throw new Error(`Open-Meteo climate HTTP ${res.status}`);
  const json = (await res.json()) as {
    daily?: { temperature_2m_mean?: (number | null)[]; precipitation_sum?: (number | null)[] };
  };
  const temps = (json.daily?.temperature_2m_mean ?? []).filter(
    (v): v is number => typeof v === "number",
  );
  const precip = (json.daily?.precipitation_sum ?? []).filter(
    (v): v is number => typeof v === "number",
  );
  if (!temps.length) throw new Error("Open-Meteo climate returned no temperatures");
  return summarizeDaily(temps, precip);
}

export function scoreStress(
  baseline: ClimateNormals,
  projected: ClimateNormals,
): {
  heatDeltaC: number;
  precipChangePct: number;
  heatScore: number;
  droughtScore: number;
  extremePrecipScore: number;
  overallScore: number;
} {
  const heatDeltaC = projected.meanTempC - baseline.meanTempC;
  const precipChangePct =
    ((projected.precipMmYear - baseline.precipMmYear) / Math.max(baseline.precipMmYear, 1)) *
    100;

  const heatScore = Math.min(
    100,
    Math.max(0, heatDeltaC * 28 + (projected.hotDaysApprox - baseline.hotDaysApprox) * 1.2),
  );
  const droughtScore = Math.min(
    100,
    Math.max(0, precipChangePct < 0 ? Math.abs(precipChangePct) * 3.2 : 10),
  );
  // Proxy: hotter + wetter spells → extreme precip risk rises even if annual mean drops modestly
  const extremePrecipScore = Math.min(
    100,
    Math.max(0, heatDeltaC * 12 + (precipChangePct > 0 ? precipChangePct * 1.5 : 18)),
  );
  const overallScore = Number(
    (heatScore * 0.4 + droughtScore * 0.4 + extremePrecipScore * 0.2).toFixed(0),
  );

  return {
    heatDeltaC: Number(heatDeltaC.toFixed(2)),
    precipChangePct: Number(precipChangePct.toFixed(1)),
    heatScore: Number(heatScore.toFixed(0)),
    droughtScore: Number(droughtScore.toFixed(0)),
    extremePrecipScore: Number(extremePrecipScore.toFixed(0)),
    overallScore,
  };
}
