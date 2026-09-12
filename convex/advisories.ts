import { v } from "convex/values";
import { internalMutation, mutation, query } from "./_generated/server";

const advisoryDoc = v.object({
  _id: v.id("advisories"),
  _creationTime: v.number(),
  location: v.string(),
  mode: v.string(),
  verdict: v.optional(v.string()),
  mostExposed: v.optional(v.string()),
  signals: v.optional(v.array(v.string())),
  summerBalanceMm: v.optional(v.number()),
  text: v.string(),
});

/**
 * Latest action plans across all fields.
 *
 * Subscribed to by the UI, so a plan generated in one browser session appears
 * in every other one without polling or a websocket of our own.
 */
export const recent = query({
  args: { limit: v.optional(v.number()) },
  returns: v.array(advisoryDoc),
  handler: async (ctx, args) => {
    return await ctx.db.query("advisories").order("desc").take(args.limit ?? 8);
  },
});

export const forLocation = query({
  args: { location: v.string(), limit: v.optional(v.number()) },
  returns: v.array(advisoryDoc),
  handler: async (ctx, args) => {
    return await ctx.db
      .query("advisories")
      .withIndex("by_location", (q) => q.eq("location", args.location))
      .order("desc")
      .take(args.limit ?? 5);
  },
});

export const add = mutation({
  args: {
    location: v.string(),
    mode: v.string(),
    verdict: v.optional(v.string()),
    mostExposed: v.optional(v.string()),
    signals: v.optional(v.array(v.string())),
    summerBalanceMm: v.optional(v.number()),
    text: v.string(),
  },
  returns: v.id("advisories"),
  handler: async (ctx, args) => {
    return await ctx.db.insert("advisories", args);
  },
});

/**
 * Wipe the advisory feed so a demo run starts empty.
 *
 * Internal on purpose: resetting the feed should only ever be possible from
 * the CLI, never from the app.
 */
export const clear = internalMutation({
  args: {},
  returns: v.number(),
  handler: async (ctx) => {
    const rows = await ctx.db.query("advisories").collect();
    for (const row of rows) {
      await ctx.db.delete(row._id);
    }
    return rows.length;
  },
});
