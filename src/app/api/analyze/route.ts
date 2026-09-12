import { NextResponse } from "next/server";
import { analyzeField } from "@/lib/analyze";
import type { AnalyzeRequest, CropId, HorizonId } from "@/lib/types";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const CROPS: CropId[] = ["maize", "wheat", "sunflower"];
const HORIZONS: HorizonId[] = ["2030s", "2050s"];

export async function POST(req: Request) {
  try {
    const body = (await req.json()) as Partial<AnalyzeRequest>;
    const lat = Number(body.lat);
    const lon = Number(body.lon);
    const crop = body.crop as CropId;
    const horizon = (body.horizon as HorizonId) ?? "2050s";

    if (!Number.isFinite(lat) || !Number.isFinite(lon)) {
      return NextResponse.json({ error: "lat and lon are required" }, { status: 400 });
    }
    if (lat < -90 || lat > 90 || lon < -180 || lon > 180) {
      return NextResponse.json({ error: "lat/lon out of range" }, { status: 400 });
    }
    if (!CROPS.includes(crop)) {
      return NextResponse.json({ error: "crop must be maize|wheat|sunflower" }, { status: 400 });
    }
    if (!HORIZONS.includes(horizon)) {
      return NextResponse.json({ error: "horizon must be 2030s|2050s" }, { status: 400 });
    }

    const result = await analyzeField({
      lat,
      lon,
      crop,
      horizon,
      telemetry: body.telemetry,
      useFixture: body.useFixture,
      parcelId: body.parcelId,
    });

    return NextResponse.json(result);
  } catch (err) {
    console.error("[api/analyze]", err);
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "analyze failed" },
      { status: 500 },
    );
  }
}
