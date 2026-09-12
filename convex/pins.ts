import { v } from "convex/values";
import { mutation, query } from "./_generated/server";

/** All field records, in the shape agrisense and the Streamlit UI expect. */
export const list = query({
  args: {},
  returns: v.array(v.any()),
  handler: async (ctx) => {
    const rows = await ctx.db.query("pins").collect();
    return rows.map((row) => row.record);
  },
});

export const get = query({
  args: { name: v.string() },
  returns: v.any(),
  handler: async (ctx, args) => {
    const row = await ctx.db
      .query("pins")
      .withIndex("by_name", (q) => q.eq("name", args.name))
      .unique();
    return row ? row.record : null;
  },
});

/** Idempotent so the seed script can be re-run without duplicating rows. */
export const upsert = mutation({
  args: {
    name: v.string(),
    region: v.optional(v.string()),
    lat: v.number(),
    lon: v.number(),
    record: v.any(),
  },
  returns: v.id("pins"),
  handler: async (ctx, args) => {
    const existing = await ctx.db
      .query("pins")
      .withIndex("by_name", (q) => q.eq("name", args.name))
      .unique();

    if (existing) {
      await ctx.db.patch(existing._id, args);
      return existing._id;
    }
    return await ctx.db.insert("pins", args);
  },
});
