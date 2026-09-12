/**
 * future: LinkedIn agritech company intel
 *
 * Hook for a later LinkedIn (or similar) scraper / company-intel agent that
 * enriches adaptation plans with nearby agritech vendors, co-ops, and
 * extension partners. Intentionally NOT implemented for the hackathon MVP.
 */

export type AgritechCompanyIntel = {
  companyName: string;
  focus: string;
  region?: string;
  profileUrl?: string;
  relevanceNote?: string;
};

export type LinkedInIntelRequest = {
  lat: number;
  lon: number;
  crop: string;
  horizon: string;
  keywords?: string[];
};

export async function fetchAgritechCompanyIntel(
  _req: LinkedInIntelRequest,
): Promise<{
  status: "stub";
  todo: string;
  results: AgritechCompanyIntel[];
}> {
  return {
    status: "stub",
    todo: "future: LinkedIn agritech company intel — plug scraper/agent here",
    results: [],
  };
}
