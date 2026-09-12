import fixtures from "@/data/fixtures/parcels.json";
import { rankAdaptations } from "./adapt";
import { DATA_CREDITS, DISCLAIMER } from "./credits";
import { fetchAgritechCompanyIntel } from "./linkedin-stub";
import {
  fetchBaselineClimate,
  fetchProjectedClimate,
  scoreStress,
} from "./openmeteo";
import { findParcel, nearestParcel } from "./parcels";
import { fetchSoilGrids } from "./soilgrids";
import type {
  AnalyzeRequest,
  AnalyzeResult,
  ClimateNormals,
  HorizonId,
  SoilSnapshot,
} from "./types";

type FixtureParcel = {
  soil: SoilSnapshot;
  baseline: ClimateNormals;
  projected: Record<HorizonId, ClimateNormals>;
};

function fixtureFor(
  parcelId: string | undefined,
  lat: number,
  lon: number,
): { id: string; name?: string; data: FixtureParcel } {
  const parcel = findParcel(parcelId) ?? nearestParcel(lat, lon);
  const data = (fixtures.parcels as Record<string, FixtureParcel>)[parcel.id];
  if (!data) throw new Error(`Missing fixture for parcel ${parcel.id}`);
  return { id: parcel.id, name: parcel.name, data };
}

function forceFixtures(): boolean {
  return process.env.USE_FIXTURES === "1" || process.env.USE_FIXTURES === "true";
}

export async function analyzeField(
  req: AnalyzeRequest,
): Promise<AnalyzeResult> {
  const useFixture = Boolean(req.useFixture) || forceFixtures();
  const telemetry = req.telemetry ?? {};
  let mode: AnalyzeResult["mode"] = "live";
  let soil: SoilSnapshot;
  let baseline: ClimateNormals;
  let projected: ClimateNormals;
  let parcelName: string | undefined;

  if (useFixture) {
    mode = "fixture";
    const fx = fixtureFor(req.parcelId, req.lat, req.lon);
    parcelName = fx.name;
    soil = fx.data.soil;
    baseline = fx.data.baseline;
    projected = fx.data.projected[req.horizon];
  } else {
    try {
      const [soilLive, baseLive, projLive] = await Promise.all([
        fetchSoilGrids(req.lat, req.lon),
        fetchBaselineClimate(req.lat, req.lon),
        fetchProjectedClimate(req.lat, req.lon, req.horizon),
      ]);
      soil = soilLive;
      baseline = baseLive;
      projected = projLive;
    } catch (err) {
      console.warn("[analyze] live APIs failed, using fixtures:", err);
      mode = "fixture";
      const fx = fixtureFor(req.parcelId, req.lat, req.lon);
      parcelName = fx.name;
      soil = fx.data.soil;
      baseline = fx.data.baseline;
      projected = fx.data.projected[req.horizon];
    }
  }

  if (telemetry.ph != null) soil = { ...soil, ph: telemetry.ph };

  const scored = scoreStress(baseline, projected);
  const stress = { ...scored, baseline, projected };
  const actions = rankAdaptations({ crop: req.crop, soil, stress, telemetry });

  await fetchAgritechCompanyIntel({
    lat: req.lat,
    lon: req.lon,
    crop: req.crop,
    horizon: req.horizon,
  });

  return {
    mode,
    parcelName,
    location: { lat: req.lat, lon: req.lon },
    crop: req.crop,
    horizon: req.horizon,
    soil,
    stress,
    actions,
    telemetryApplied: telemetry,
    credits: [...DATA_CREDITS],
    disclaimer: DISCLAIMER,
    fetchedAt: new Date().toISOString(),
  };
}
