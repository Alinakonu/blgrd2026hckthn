import { httpRouter } from "convex/server";
import { httpAction } from "./_generated/server";
import { api } from "./_generated/api";

/**
 * Tiny HTTP bridge so Streamlit (Python) can talk to Convex.
 *
 * After `npx convex dev`, copy the HTTP Actions URL
 * (https://<deployment>.convex.site) into CONVEX_SITE_URL.
 */
const http = httpRouter();

function json(data: unknown, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
    },
  });
}

function checkToken(request: Request): boolean {
  const expected = process.env.PLOTS_HTTP_TOKEN;
  if (!expected) return true; // open for local hackathon demos
  const got = request.headers.get("x-plots-token") || "";
  return got === expected;
}

http.route({
  path: "/plots",
  method: "GET",
  handler: httpAction(async (ctx, request) => {
    if (!checkToken(request)) return json({ error: "unauthorized" }, 401);
    const plots = await ctx.runQuery(api.plots.list, {});
    return json({ backend: "convex", plots });
  }),
});

http.route({
  path: "/plots",
  method: "POST",
  handler: httpAction(async (ctx, request) => {
    if (!checkToken(request)) return json({ error: "unauthorized" }, 401);
    let body: Record<string, unknown>;
    try {
      body = await request.json();
    } catch {
      return json({ error: "invalid JSON" }, 400);
    }
    const required = [
      "label",
      "pinName",
      "region",
      "lat",
      "lon",
      "summerBalanceMm",
      "hotDays30",
      "hotDays35",
      "verdict",
    ] as const;
    for (const key of required) {
      if (body[key] === undefined || body[key] === null || body[key] === "") {
        return json({ error: `missing field: ${key}` }, 400);
      }
    }
    const id = await ctx.runMutation(api.plots.save, {
      label: String(body.label),
      pinName: String(body.pinName),
      region: String(body.region),
      lat: Number(body.lat),
      lon: Number(body.lon),
      summerBalanceMm: Number(body.summerBalanceMm),
      hotDays30: Number(body.hotDays30),
      hotDays35: Number(body.hotDays35),
      verdict: String(body.verdict),
    });
    return json({ backend: "convex", id });
  }),
});

http.route({
  path: "/plots",
  method: "OPTIONS",
  handler: httpAction(async () => {
    return new Response(null, {
      status: 204,
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, x-plots-token",
      },
    });
  }),
});

export default http;
