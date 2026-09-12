# Convex integration — why, what, and the 45-minute path

Written so the integration is defensible rather than decorative. A judge will ask why Convex is here; "for the partner prize" is not an answer, and bolt-on usage is easy to spot.

---

## 1. The honest case for Convex

Two problems in the current build are exactly what Convex is for.

**Advice has no memory.** Generated action plans live in `st.session_state`. They die on refresh, are invisible to anyone else, and leave no record of which data produced which recommendation. That last point matters more than it sounds: the entire design rule in `docs/LLM_PROMPT.md` is that every number must be traceable. Right now we can claim traceability but cannot demonstrate it, because nothing is stored. Convex's own pitch lists "agent memory: store runs, tools, and threads" — that is precisely the gap.

**The data pipeline cannot sit in the request path.** `build_pins.py` takes 33–114 seconds per location and hits Open-Meteo 429s. We solved that by committing a static `data/pins.json`, which is a hack we openly documented in `docs/DATA_LIMITS.md`. A database with reactive queries is the correct shape for slow ingest feeding a live UI.

So the integration is not "we added a database." It is: **the analysis is slow and the advice needs an audit trail, so the store is reactive and the history is queryable.**

## 2. What was built

Additive only. Nothing existing was replaced, and the app still runs with Convex absent.

| File | Role |
| --- | --- |
| `convex/schema.ts` | Two tables: `pins` (field records) and `advisories` (agent memory) |
| `convex/pins.ts` | `list`, `get`, `upsert` — upsert is idempotent so seeding can re-run |
| `convex/advisories.ts` | `recent`, `forLocation`, `add` |
| `agrisense/store.py` | Data access with automatic fallback to `data/pins.json` |
| `scripts/push_to_convex.py` | Seeds the deployment and verifies the read-back |
| `app.py` | Loads via `store`, logs each plan, shows a live feed |

The `pins` table stores the whole analysis document in a `record` field, so the contract from `PLAN.md` section 2 is unchanged. Nothing downstream has to know where the data came from.

### The fallback is the important part

`agrisense/store.py` never raises on a Convex failure. Reads fall back to the committed JSON; writes are best-effort and return a boolean. The client is cached including its failure state, so a missing package costs one attempt rather than one per Streamlit rerun.

Verified with no `CONVEX_URL` set:

```
pins: 6 source: local
status: {'connected': False, 'url': None, 'detail': 'CONVEX_URL not set'}
advisories: []
```

That is the pre-Convex behaviour exactly. **If the integration fails on the day, the demo does not notice.**

## 3. Setup — the one real blocker

**Node is not installed on this machine.** Convex's CLI needs it to deploy functions; there is no way around that, since the HTTP API can only call functions that already exist.

This is a much lighter ask than the God's Eye View toolchain we rejected in `docs/GEV_DECISION.md` — one npm package and a CLI, not Cesium plus Puppeteer plus Sharp — but it is still the step that can eat the budget. Do it first, and if it stalls, stop: the app already works.

```powershell
# 1. Node (once) — winget is available on this machine
winget install OpenJS.NodeJS.LTS
#    then reopen the terminal so PATH picks it up

# 2. Convex deployment — opens a browser to log in,
#    creates the project, writes .env.local with CONVEX_URL
npm install
npx convex dev

# 3. Python client
pip install convex

# 4. Seed and verify (separate terminal; leave convex dev running)
python scripts/push_to_convex.py
```

The official Cursor rules are already vendored at `.cursor/rules/convex_rules.mdc`, scoped by frontmatter to `.ts/.tsx/.js/.jsx`, so they guide Convex work without interfering with the Python side. Our functions follow them, including the mandatory `returns` validator on every query and mutation and the `by_<field>` index naming convention.

Once Node is installed, `npx convex ai-files install` will additionally maintain `AGENTS.md` and generated guidelines if you want them.

A successful seed prints `Wrote 6 pins.` followed by `Read back 6 pins from 'convex'.` If it says `local` instead, the deployment is not reachable and the app will simply keep using the file.

## 4. The demo moment

Reactivity has to be *seen* or it does not count. The cheapest convincing version takes ten seconds:

1. Open the app in two browser windows, side by side.
2. Generate a plan for Novi Sad in the left window.
3. It appears in the right window's "Recent plans (live)" list.

No polling loop, no websocket code of ours. That is the whole point of the partner technology, shown rather than described.

For the pitch, one line: *"Plans are stored as agent memory in Convex, so every recommendation keeps the data snapshot that produced it — and any device watching sees it immediately."*

## 5. Honest limits

`st.cache_data` on `load_pins` means the pin list is not live — only the advisory feed is, and it refreshes on Streamlit's normal rerun rather than pushing. Convex's Python client does support true streaming via `client.subscribe()`, but that is a blocking generator and wiring it into Streamlit's execution model is not a 45-minute job. **Do not claim live-updating field data.** The advisory feed is the real reactive surface; describe that and nothing more.

Auth is not wired up. Multi-farmer row scoping is a natural next step and is worth mentioning as roadmap, not as something built.

## 6. Decision checklist

Take this on only if all three hold:

- [ ] Core demo already works and has been recorded as a backup
- [ ] At least 45 minutes left, unhurried
- [ ] Someone is willing to install Node

If any fails, skip it. A working offline demo beats a half-wired backend, and `store.py` is written so the integration can be finished later without touching anything else.
