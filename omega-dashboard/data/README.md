# Omega Dashboard — `data/status.json` feed format

The dashboard page (`index.html`) has NO backend. It renders whatever is in
`data/status.json`, refreshed by JavaScript every 60 seconds. Any cron worker
or lane agent can regenerate this file (and commit + push the repo, same as the
night-desk deploy) to put live data on the TV screen.

## Rules (load-bearing)

1. **Honest values only.** `verified_total_usd` = money actually received /
   confirmed via a primary record (Plaid balance, payout receipt, Sent log).
   Never project, annualize, or estimate. If nothing verified, it is `0.0`.
2. **No personal identifiers.** No email, phone, street address, kids' names,
   DOBs, account numbers, order codes. The dashboard is designed to be
   PII-free; it sits on a public URL.
3. **`meta.sample: true`** = every number on screen is a placeholder. Workers
   writing real data MUST set `"sample": false` and set
   `generated_at`/`generated_by`. The page shows a SAMPLE banner whenever
   `meta.sample` is true (or the fetch fails).
4. Keep the file small (< 64 KB). TV browsers have limited memory.

## Schema (v1)

```jsonc
{
  "meta": {
    "schema_version": 1,
    "generated_at": "2026-10-15T19:55:00-04:00",   // ISO-8601, owner TZ
    "generated_by": "worker-name",
    "sample": false,                                // true = placeholder data
    "note": "optional human note"
  },
  "fleet": {
    "summary": "healthy | degraded | down",         // one-word rollup
    "browser_fleet": "up | down",                   // live-browser availability
    "note": "short plain-text note"
  },
  "agents": [
    {
      "id": "referral-hunt",                        // stable machine id
      "label": "Referral Hunt",                      // human label
      "status": "ok | warn | down | idle",          // one of four
      "current_task": "plain-text, <= 80 chars",
      "last_update": "19:53 EDT"
    }
  ],
  "earnings": {
    "verified_total_usd": 0.00,
    "pending_usd": 0.00,                            // claimed/filed, not yet received
    "currency": "USD",
    "events": [
      {"time": "...", "lane": "...", "amount_usd": 0.00,
       "state": "verified | pending | sample", "note": "..."}
    ]
  },
  "discoveries": [
    {"time": "...", "lane": "...", "text": "<= 120 chars, verified fact only"}
  ],
  "deadlines": [
    {"title": "...", "due": "2026-10-21 12:00 PM ET",
     "status": "upcoming | overdue", "note": "..."}
  ],
  "errors": [
    {"time": "...", "source": "...", "message": "<= 120 chars",
     "impact": "none | delayed | blocked"}
  ],
  "approvals": [
    // DISPLAY-ONLY. Listed asks are answered IN CHAT, never from this page.
    {"id": "unique-id", "title": "...", "detail": "<= 140 chars",
     "asked_at": "2026-10-15 19:50 EDT"}
  ],
  "tokens": {
    "banked_billions": 4.0,
    "reset_at": "2026-10-17T17:05:00-04:00",
    "note": "..."
  }
}
```

## Companion files (standalone panels)

Four more panels render from their own JSON files, fetched directly by
`index.html` every 60s — they are NOT merged into `status.json`. Same rules
(honest values, no PII, < 64 KB each).

- `data/ai-network.json` — `{fallback_order: [...], routes: [{order, provider, model, auth: "keyed-required | keyless", status, note}], rules: [...]}`.
  Provider/model names and status words ONLY — no keys, tokens, or credentials.
  Source: `~/workspace/omega-ecosystem/ai-routes/`.
- `data/workstreams.json` — `{workstreams: [{id: "A".. "H", label, status, note}]}`. Status labels: `deployed | ok | warn | pending`.
- `data/social.json` — `{platforms: [{platform, status: "proposed | active | live", note}]}`.
  If `~/workspace/omega-ecosystem/social-brand/brand-plan-2026-10-16.md` is
  absent, every platform is `proposed`.
- `data/revenue.json` — `{verified_received_usd, currency: "USD", opportunities: [{name, type, prize_usd|null, status, note}], rule}`.
  Honest zero: `verified_received_usd` = cash actually received from
  operations ($0.00 to date). Opportunities are identified, not earnings.

## How workers publish updates

1. Edit or regenerate `data/status.json` in this dashboard directory.
2. Validate: `python3 -c "import json; json.load(open('data/status.json'))"`.
3. Deploy via the GitHub Pages repo (see `../DEPLOY.md`): copy
   `dashboard/*` over the `omega-dashboard/` folder in the local clone of
   `midnightmichigan.github.io`, commit, push. TV picks it up within
   ~1–2 minutes (GitHub Pages rebuild) + the 60s page auto-refresh.

There is deliberately no write path FROM the TV back to the system: a static
page cannot submit approvals without a backend, and adding one would create an
unauthenticated action endpoint on a public URL. Approvals happen in chat.
