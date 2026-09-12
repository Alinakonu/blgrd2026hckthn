import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

/**
 * Tiny plot locker for the hackathon demo.
 * Streamlit (or any client) saves the current pin as a "farmer plot".
 */
export default defineSchema({
  plots: defineTable({
    label: v.string(),
    pinName: v.string(),
    region: v.string(),
    lat: v.number(),
    lon: v.number(),
    summerBalanceMm: v.number(),
    hotDays30: v.number(),
    hotDays35: v.number(),
    verdict: v.string(),
    savedAt: v.number(),
  }).index("by_savedAt", ["savedAt"]),
});
