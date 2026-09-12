import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  // One row per field/location. `record` holds the full analysis document that
  // agrisense produces, so the Python side and the UI keep the exact shape
  // defined in PLAN.md section 2.
  pins: defineTable({
    name: v.string(),
    region: v.optional(v.string()),
    lat: v.number(),
    lon: v.number(),
    record: v.any(),
  }).index("by_name", ["name"]),

  // Agent memory: every action plan that was generated, with the inputs that
  // produced it. This is what makes advice auditable -- a judge asking "where
  // did this number come from" can be shown the stored data snapshot.
  advisories: defineTable({
    location: v.string(),
    mode: v.string(), // "llm" | "offline" | "offline_fallback"
    verdict: v.optional(v.string()),
    mostExposed: v.optional(v.string()),
    signals: v.optional(v.array(v.string())),
    summerBalanceMm: v.optional(v.number()),
    text: v.string(),
  }).index("by_location", ["location"]),
});
