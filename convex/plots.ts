import { v } from "convex/values";
import { mutation, query } from "./_generated/server";

export const save = mutation({
  args: {
    label: v.string(),
    pinName: v.string(),
    region: v.string(),
    lat: v.number(),
    lon: v.number(),
    summerBalanceMm: v.number(),
    hotDays30: v.number(),
    hotDays35: v.number(),
    verdict: v.string(),
  },
  handler: async (ctx, args) => {
    const id = await ctx.db.insert("plots", {
      ...args,
      savedAt: Date.now(),
    });
    return id;
  },
});

export const list = query({
  args: {},
  handler: async (ctx) => {
    const rows = await ctx.db.query("plots").withIndex("by_savedAt").order("desc").take(50);
    return rows;
  },
});

export const clear = mutation({
  args: {},
  handler: async (ctx) => {
    const rows = await ctx.db.query("plots").collect();
    for (const row of rows) {
      await ctx.db.delete(row._id);
    }
    return rows.length;
  },
});
