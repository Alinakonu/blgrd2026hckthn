"use client";

/**
 * future: LinkedIn agritech company intel
 * Visible hook in the UI so judges/teammates see where vendor intel will plug in.
 */
export default function LinkedInIntelStub() {
  return (
    <aside className="border border-dashed border-[var(--rule-strong)] bg-[var(--panel-muted)] p-4 text-sm">
      <p className="text-xs uppercase tracking-[0.18em] text-[var(--muted)]">
        future: LinkedIn agritech company intel
      </p>
      <p className="mt-2 text-[var(--ink-soft)]">
        Stub only — later this panel will list nearby agritech companies, co-ops,
        and extension partners for the pinned field. API hook:{" "}
        <code className="text-[var(--accent)]">/api/linkedin-intel</code> ·{" "}
        <code className="text-[var(--accent)]">src/lib/linkedin-stub.ts</code>
      </p>
    </aside>
  );
}
