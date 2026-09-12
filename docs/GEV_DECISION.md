# God's Eye View — fork or not (B4)

**Recommendation: do not fork it. Build the Streamlit app, and reconsider only if everything else is finished and working.**

This is a data-side assessment of what integration would actually cost and what it would add.

---

## 1. What it is

[God's Eye View](https://github.com/bilawalsidhu/gods-eye-view) is a CesiumJS spatial-intelligence globe — vanilla JS, Vite, photorealistic 3D tiles, live aircraft, ships, satellites, earthquakes and public cameras, with an optional realtime voice agent. It is MIT licensed, genuinely impressive, and at ~28k stars a project people recognise.

From `package.json`: six runtime dependencies (`cesium ^1.124`, `satellite.js`, `@mapbox/vector-tile`, `pbf`, `mgrs`, `egm96-universal`), Vite 6, plus `puppeteer` and `sharp` in devDependencies. Engines are pinned to **Node >=24.14 <25 or >=26 <27**.

## 2. The blocking cost

**Node is not installed on this machine.** `node` and `npm` are both unrecognised commands.

So the integration path does not start at "clone and run." It starts at installing a specific Node major version, then `npm ci` pulling Cesium plus Puppeteer and Sharp — both of which fetch platform binaries and are among the slower installs in the npm ecosystem — then `npm run doctor`, then finding out whether the app boots on this machine. That is the 15-minute timebox from `PLAN.md` spent before a single line of AgriSense code exists, with a real chance of ending at a Node version error rather than a globe.

Against that, our Python side needs no installs at all: `agrisense/` is stdlib-only and `data/pins.json` is committed.

## 3. The data-side argument against

Even assuming it installs cleanly, the fit is poor for what we have:

**Six points do not need a globe.** The dataset is six Serbian cities. Cesium's value is continuous spatial data at scale — aircraft tracks, satellite shells, tile pyramids. Six markers on a photorealistic 3D Earth is a lot of machinery to display what a static map image shows equally well.

**Our finding is a time series, not a geography.** The pitch is "rainfall looks flat while the growing season dried out." That lives in a two-line chart of rainfall against ET0 across two decades. A globe cannot show it. We would be adding a spatial visualisation to carry an argument that is fundamentally temporal.

**The data is not interactive-speed.** A full `build_pin` takes 33–114 seconds because of Open-Meteo's rate limits. Click-anywhere-on-Earth is exactly the interaction a globe invites and exactly the one we cannot serve. We would build an interface that promises responsiveness the backend cannot deliver.

**It splits the stack.** Our analysis is Python. GEV is vanilla JS with server-side key brokering. Integrating means standing up a Python API, wiring a Vite proxy, and matching two dependency and runtime stories — on a clock, for a visual layer.

## 4. What to do instead

Keep the whole thing in Streamlit and spend the time on the argument rather than the globe:

- The rainfall-versus-ET0 chart across two decades. This is the pitch; it deserves the polish budget.
- `st.map` or a static Serbia image with six markers coloured by exposure band. Minutes of work, and it conveys the north-south split — Vojvodina deteriorating, Belgrade and Niš stable — as well as a 3D globe would.
- The crop exposure table and the LLM action plan.

## 5. If it is revisited

Only with the core demo finished and recorded. In that case the cheapest version is **not a fork**: run GEV unmodified, fly it to a Serbian field, and screen-record ten seconds as a pitch opener. That buys the visual impact without owning the integration.

An actual fork means disabling the irrelevant layers (flights, AIS, CCTV, satellites), adding one module under `src/data/` on the layer interface (`init`/`enable`/`disable`/`update`/`destroy`/`getStats`), serving `pins.json` from a local endpoint, and registering attribution in `DATA_SOURCES.md` and `dataCredits.js` as `CONTRIBUTING.md` requires. That is a project, not a task.

## 6. Recorded decision

| | |
| --- | --- |
| **Decision** | Out of scope for the hackathon build |
| **Primary reason** | Node not installed; heavy toolchain before any AgriSense code |
| **Secondary reason** | Six points and a temporal finding do not need a 3D globe |
| **Revisit if** | Core demo done, recorded, and time remains |
| **Cheapest fallback** | Unmodified GEV screen-recording as a pitch opener |
