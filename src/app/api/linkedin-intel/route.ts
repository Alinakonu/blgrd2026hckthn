/**
 * future: LinkedIn agritech company intel — API surface for the stub.
 * Returns empty results until a scraper/agent is plugged in.
 */
import { NextResponse } from "next/server";
import { fetchAgritechCompanyIntel } from "@/lib/linkedin-stub";

export const dynamic = "force-dynamic";

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const lat = Number(searchParams.get("lat") ?? "45.2671");
  const lon = Number(searchParams.get("lon") ?? "19.8335");
  const crop = searchParams.get("crop") ?? "maize";
  const horizon = searchParams.get("horizon") ?? "2050s";

  const payload = await fetchAgritechCompanyIntel({ lat, lon, crop, horizon });
  return NextResponse.json(payload);
}
