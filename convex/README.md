# Convex integration (optional / next step)

SoilShift is structured so plans can be saved to **Convex** without rewriting the UI.

## Suggested shape

- `plans` table: `{ lat, lon, crop, horizon, resultJson, createdAt }`
- Mutation `savePlan` called after `/api/analyze` succeeds
- Query `listPlans` for a simple “saved fields” list

## Setup

```bash
npm install convex
npx convex dev
```

Point `NEXT_PUBLIC_CONVEX_URL` in `.env.local`, then wire a client provider in `src/app/layout.tsx`.

This folder is a placeholder so the team can claim the Convex prize path without blocking the map → stress → checklist happy path.
