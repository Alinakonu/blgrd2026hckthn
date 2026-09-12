import type {
  AdaptationAction,
  ClimateStress,
  CropId,
  SoilSnapshot,
  SoilTelemetry,
} from "./types";

type RankContext = {
  crop: CropId;
  soil: SoilSnapshot;
  stress: ClimateStress;
  telemetry: SoilTelemetry;
};

const CITE = {
  fao: {
    label: "FAO climate-smart agriculture",
    url: "https://www.fao.org/climate-smart-agriculture/en/",
  },
  soilgrids: {
    label: "ISRIC SoilGrids",
    url: "https://www.isric.org/explore/soilgrids",
  },
  openMeteo: {
    label: "Open-Meteo Climate API",
    url: "https://open-meteo.com/en/docs/climate-api",
  },
  cover: {
    label: "USDA cover crops overview",
    url: "https://www.nrcs.usda.gov/conservation-basics/natural-resource-concerns/soil/cover-crops",
  },
};

function clampPriority(score: number): AdaptationAction["priority"] {
  if (score >= 70) return "high";
  if (score >= 40) return "medium";
  return "low";
}

/** Deterministic ranked adaptation checklist. */
export function rankAdaptations(ctx: RankContext): AdaptationAction[] {
  const { crop, soil, stress, telemetry } = ctx;
  const ph = telemetry.ph ?? soil.ph ?? 7;
  const soc = soil.socGPerKg ?? 12;
  const sand = soil.sandPct ?? 35;
  const candidates: (AdaptationAction & { score: number })[] = [];

  {
    const score =
      (soc < 15 ? 35 : 15) +
      stress.droughtScore * 0.35 +
      (telemetry.organicMatterPct != null && telemetry.organicMatterPct < 2
        ? 20
        : 0);
    candidates.push({
      id: "build-om",
      title: "Build soil organic matter (residue + compost)",
      rank: 0,
      priority: clampPriority(score),
      score,
      why: `Projected drought stress ${stress.droughtScore}/100 and SOC ≈ ${soc.toFixed(1)} g/kg. Higher OM improves water holding before ${crop} yields slip.`,
      how: "Keep more residue; add composted manure where available; avoid burning stubble; track OM every 2–3 seasons.",
      cites: [CITE.fao, CITE.soilgrids],
      drivers: ["drought", "soc"],
    });
  }

  {
    const score =
      stress.extremePrecipScore * 0.25 +
      stress.droughtScore * 0.3 +
      (sand > 40 ? 20 : 10) +
      (crop === "maize" ? 12 : 8);
    candidates.push({
      id: "cover-crops",
      title: "Add winter / shoulder-season cover crops",
      rank: 0,
      priority: clampPriority(score),
      score,
      why: `Heat +${stress.heatDeltaC}°C and precip change ${stress.precipChangePct}% raise erosion and bare-soil bake risk between cash crops.`,
      how: "Try vetch–rye or clover mixes after harvest; terminate before your planting window.",
      cites: [CITE.cover, CITE.openMeteo],
      drivers: ["heat", "extreme-precip", "texture"],
    });
  }

  {
    const score =
      stress.droughtScore * 0.55 +
      stress.heatScore * 0.25 +
      (crop === "maize" ? 15 : crop === "sunflower" ? 8 : 10);
    candidates.push({
      id: "irrigation-timing",
      title: "Shift irrigation timing to critical growth stages",
      rank: 0,
      priority: clampPriority(score),
      score,
      why: `Drought score ${stress.droughtScore}/100 under this horizon. For ${crop}, protect flowering / grain fill rather than watering evenly all season.`,
      how: "Map phenology windows; prefer early-morning sets; mulch to cut evaporative loss if irrigating.",
      cites: [CITE.fao, CITE.openMeteo],
      drivers: ["drought", "heat", "crop"],
    });
  }

  {
    const score =
      stress.droughtScore * 0.2 +
      (soc < 16 ? 25 : 10) +
      stress.extremePrecipScore * 0.2;
    candidates.push({
      id: "reduce-tillage",
      title: "Reduce tillage intensity",
      rank: 0,
      priority: clampPriority(score),
      score,
      why: "Less inversion keeps structure and residue cover that buffers hotter summers and bursty rain.",
      how: "Move toward strip-till or no-till where weeds/equipment allow; start on one block to learn.",
      cites: [CITE.fao],
      drivers: ["structure", "drought"],
    });
  }

  {
    let score = 15;
    let title = "Hold pH; retest in 2 seasons";
    let why = `Current pH ≈ ${ph.toFixed(1)} looks workable for ${crop}.`;
    let how = "Sample 0–20 cm after harvest; avoid blanket lime without a lab test.";
    if (ph < 5.8) {
      score = 70 + (5.8 - ph) * 10;
      title = "Lime to lift acidic topsoil";
      why = `pH ≈ ${ph.toFixed(1)} can lock phosphorus and stress ${crop} roots as heat rises.`;
      how = "Apply agricultural lime based on buffer pH; incorporate lightly; retest next year.";
    } else if (ph > 7.8) {
      score = 55 + (ph - 7.8) * 12;
      title = "Address alkaline / calcareous constraints";
      why = `pH ≈ ${ph.toFixed(1)} may limit micronutrients (Fe, Zn) under hotter, drier spells.`;
      how = "Prefer acidifying N forms carefully; consider gypsum only if sodicity is confirmed.";
    }
    candidates.push({
      id: "ph-amendment",
      title,
      rank: 0,
      priority: clampPriority(score),
      score,
      why,
      how,
      cites: [CITE.soilgrids, CITE.fao],
      drivers: ["ph", "telemetry"],
    });
  }

  if (
    telemetry.n != null ||
    telemetry.p != null ||
    telemetry.k != null ||
    telemetry.moisture != null
  ) {
    const n = telemetry.n ?? 40;
    const pVal = telemetry.p ?? 40;
    const k = telemetry.k ?? 40;
    const moist = telemetry.moisture ?? 50;
    let score = 40;
    let title = "Tune NPK to crop demand + moisture";
    let why = `Telemetry N=${n}, P=${pVal}, K=${k}, moisture=${moist}. Pair fertilizer with water-limited seasons.`;
    let how = "Split N; avoid large single shots before heat waves; match P/K to soil test.";
    if (n > 80 && moist < 40) {
      score = 75;
      title = "Cut surplus N under dry outlook";
      why = `High N (${n}) with low moisture (${moist}) raises lodging / burn risk as heat increases.`;
      how = "Reduce pre-plant N 15–25%; favor in-season checks.";
    } else if (pVal < 25) {
      score = 68;
      title = "Correct low phosphorus starter";
      why = `Low P (${pVal}) limits early rooting — worse when springs warm faster.`;
      how = "Band P near seed; confirm with soil lab.";
    } else if (k < 25 && crop === "maize") {
      score = 65;
      title = "Restore potassium for maize stress tolerance";
      why = `Low K (${k}) weakens drought/heat tolerance in maize.`;
      how = "Apply K based on removal rates; watch leaf symptoms mid-season.";
    }
    candidates.push({
      id: "npk-balance",
      title,
      rank: 0,
      priority: clampPriority(score),
      score,
      why,
      how,
      cites: [CITE.fao],
      drivers: ["telemetry", "crop"],
    });
  }

  {
    const score =
      stress.heatScore * 0.45 +
      (crop === "wheat" ? 20 : crop === "maize" ? 18 : 12);
    candidates.push({
      id: "heat-practices",
      title:
        crop === "wheat"
          ? "Advance sowing / pick later-maturity buffer carefully"
          : crop === "maize"
            ? "Choose heat-tolerant hybrids + adjust plant density"
            : "Favor drought-tolerant sunflower hybrids + wider rows if needed",
      rank: 0,
      priority: clampPriority(score),
      score,
      why: `Heat score ${stress.heatScore}/100 (~${stress.projected.hotDaysApprox} hot days/yr projected vs ${stress.baseline.hotDaysApprox} baseline).`,
      how: "Talk to local seed dealers about hybrid trials in your micro-region; don't change entire acreage in year one.",
      cites: [CITE.openMeteo, CITE.fao],
      drivers: ["heat", "crop"],
    });
  }

  return candidates
    .sort((a, b) => b.score - a.score)
    .map(({ score, ...rest }, i) => ({
      ...rest,
      rank: i + 1,
      priority: clampPriority(score),
    }));
}
