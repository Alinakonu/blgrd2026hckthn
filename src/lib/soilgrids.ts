import { fetchWithTimeout } from "./retryable";
import type { SoilSnapshot } from "./types";

type SoilGridsProp = {
  depths?: { values?: { mean?: number | null } }[];
};

type SoilGridsResponse = {
  properties?: {
    layers?: {
      name: string;
      unit?: string;
      depths?: { label?: string; values?: { mean?: number | null } }[];
    }[];
  };
};

function mean0_5(layer: SoilGridsProp | undefined): number | null {
  const v = layer?.depths?.[0]?.values?.mean;
  return typeof v === "number" ? v : null;
}

function textureLabel(clay: number | null, sand: number | null, silt: number | null): string {
  if (clay == null || sand == null || silt == null) return "Unknown";
  if (clay >= 40) return "Clay";
  if (sand >= 70) return "Sandy";
  if (silt >= 50 && clay < 27) return "Silt loam";
  if (clay >= 27 && clay < 40 && sand <= 45) return "Clay loam";
  if (sand > 45 && clay < 27) return "Sandy loam";
  return "Loam";
}

/**
 * Point query against ISRIC SoilGrids REST.
 * @see https://rest.isric.org/soilgrids/v2.0/docs
 */
export async function fetchSoilGrids(lat: number, lon: number): Promise<SoilSnapshot> {
  const params = new URLSearchParams({
    lat: String(lat),
    lon: String(lon),
  });
  for (const p of ["phh2o", "soc", "clay", "sand", "silt"]) {
    params.append("property", p);
  }
  params.append("depth", "0-5cm");
  params.append("value", "mean");

  const url = `https://rest.isric.org/soilgrids/v2.0/properties/query?${params}`;
  const res = await fetchWithTimeout(url, 10_000, {
    headers: { Accept: "application/json" },
  });
  if (!res.ok) {
    throw new Error(`SoilGrids HTTP ${res.status}`);
  }
  const json = (await res.json()) as SoilGridsResponse;
  const layers = json.properties?.layers ?? [];
  const byName = Object.fromEntries(layers.map((l) => [l.name, l]));

  // SoilGrids units: phh2o is pH*10, soc is dg/kg, clay/sand/silt are g/kg
  const phRaw = mean0_5(byName.phh2o);
  const socRaw = mean0_5(byName.soc);
  const clayRaw = mean0_5(byName.clay);
  const sandRaw = mean0_5(byName.sand);
  const siltRaw = mean0_5(byName.silt);

  const clayPct = clayRaw != null ? clayRaw / 10 : null;
  const sandPct = sandRaw != null ? sandRaw / 10 : null;
  const siltPct = siltRaw != null ? siltRaw / 10 : null;

  return {
    ph: phRaw != null ? phRaw / 10 : null,
    socGPerKg: socRaw != null ? socRaw / 10 : null,
    clayPct,
    sandPct,
    siltPct,
    textureLabel: textureLabel(clayPct, sandPct, siltPct),
    source: "ISRIC SoilGrids REST",
  };
}
