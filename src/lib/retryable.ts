/**
 * Retryable loader — adapted from gods-eye-view `src/data/retryableLoad.js`.
 * Memoizes success; rate-limits failures with exponential cooldown so flaky
 * SoilGrids / Open-Meteo calls don't hammer during a live demo.
 */
export const RETRY_COOLDOWN_MS = 5_000;
export const RETRY_COOLDOWN_MAX_MS = 60_000;

export function createRetryableLoader<T>(
  load: () => Promise<T> | T,
  {
    cooldownMs = RETRY_COOLDOWN_MS,
    maxCooldownMs = RETRY_COOLDOWN_MAX_MS,
    now = () => Date.now(),
  }: {
    cooldownMs?: number;
    maxCooldownMs?: number;
    now?: () => number;
  } = {},
): () => Promise<T> {
  let inflight: Promise<T> | null = null;
  let failure: unknown = null;
  let hasFailure = false;
  let failedAt = 0;
  let consecutiveFailures = 0;
  let cached: T | undefined;
  let hasCache = false;

  return function loadOnce() {
    if (hasCache) return Promise.resolve(cached as T);
    if (inflight) return inflight;
    if (hasFailure) {
      const wait = Math.min(
        cooldownMs * 2 ** (consecutiveFailures - 1),
        maxCooldownMs,
      );
      if (now() - failedAt < wait) return Promise.reject(failure);
    }
    inflight = Promise.resolve()
      .then(() => load())
      .then((value) => {
        cached = value;
        hasCache = true;
        hasFailure = false;
        consecutiveFailures = 0;
        inflight = null;
        return value;
      })
      .catch((err) => {
        failure = err;
        hasFailure = true;
        failedAt = now();
        consecutiveFailures += 1;
        inflight = null;
        throw err;
      });
    return inflight;
  };
}

/** One-shot fetch with timeout; used by API clients. */
export async function fetchWithTimeout(
  url: string,
  ms = 8_000,
  init?: RequestInit,
): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), ms);
  try {
    return await fetch(url, { ...init, signal: controller.signal });
  } finally {
    clearTimeout(timer);
  }
}
