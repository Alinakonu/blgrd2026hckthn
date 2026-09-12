/**
 * Data attribution — pattern inspired by gods-eye-view `src/data/dataCredits.js`.
 * Keep sources visible on every analyze response.
 */
export const DATA_CREDITS = [
  {
    key: "soilgrids",
    html: 'Soil: <a href="https://www.isric.org/explore/soilgrids" target="_blank" rel="noopener">ISRIC SoilGrids</a> (CC BY 4.0)',
  },
  {
    key: "open-meteo",
    html: 'Climate: <a href="https://open-meteo.com/" target="_blank" rel="noopener">Open-Meteo</a> Historical + Climate API (CC BY 4.0)',
  },
  {
    key: "osm",
    html: 'Basemap: <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">© OpenStreetMap</a> contributors',
  },
] as const;

export const DISCLAIMER =
  "Decision support only — not a certified agronomic prescription. Always validate with local extension services and soil labs.";
