export type CropId = "maize" | "wheat" | "sunflower";

export type HorizonId = "2030s" | "2050s";

export type DataMode = "live" | "fixture";

export interface LatLon {
  lat: number;
  lon: number;
}

export interface SoilTelemetry {
  /** Optional farmer/IoT notes — AgriSense-style NPK + pH overrides */
  n?: number;
  p?: number;
  k?: number;
  ph?: number;
  moisture?: number;
  organicMatterPct?: number;
}

export interface SoilSnapshot {
  ph: number | null;
  socGPerKg: number | null;
  clayPct: number | null;
  sandPct: number | null;
  siltPct: number | null;
  textureLabel: string;
  source: string;
}

export interface ClimateNormals {
  meanTempC: number;
  precipMmYear: number;
  hotDaysApprox: number;
}

export interface ClimateStress {
  heatDeltaC: number;
  precipChangePct: number;
  heatScore: number;
  droughtScore: number;
  extremePrecipScore: number;
  overallScore: number;
  baseline: ClimateNormals;
  projected: ClimateNormals;
}

export interface AdaptationAction {
  id: string;
  title: string;
  rank: number;
  priority: "high" | "medium" | "low";
  why: string;
  how: string;
  cites: { label: string; url: string }[];
  drivers: string[];
}

export interface AnalyzeRequest {
  lat: number;
  lon: number;
  crop: CropId;
  horizon: HorizonId;
  telemetry?: SoilTelemetry;
  /** Force fixture parcel data (demo-safe). */
  useFixture?: boolean;
  parcelId?: string;
}

export interface AnalyzeResult {
  mode: DataMode;
  parcelName?: string;
  location: LatLon;
  crop: CropId;
  horizon: HorizonId;
  soil: SoilSnapshot;
  stress: ClimateStress;
  actions: AdaptationAction[];
  telemetryApplied: SoilTelemetry;
  credits: { key: string; html: string }[];
  disclaimer: string;
  fetchedAt: string;
}

export interface DemoParcel {
  id: string;
  name: string;
  region: string;
  lat: number;
  lon: number;
  defaultCrop: CropId;
  notes: string;
}
