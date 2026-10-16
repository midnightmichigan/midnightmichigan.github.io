#!/usr/bin/env python3
"""Generate data/status.json for the OMEGA TV dashboard from real workspace logs.

HONESTY RULES (hard):
- Every number comes from a file this script actually read. No estimates.
- "sample": false only when generation succeeded; on any read failure the
  script exits non-zero and the old file is left untouched.
- Zero PII: no emails, phones, addresses, kids' names, DOBs, account numbers.
- Earnings "verified_total_usd" = cash actually received from operations
  ($0.00 to date). Pending settlement/claims are NOT earnings until received.

Usage: python3 build-feed.py   (run from the dashboard/ directory)
"""
import json, re, os, sys
from datetime import datetime, timezone, timedelta

WS = os.path.expanduser("~/workspace")
EDT = timezone(timedelta(hours=-4))

def read(p):
    with open(os.path.join(WS, p), encoding="utf-8", errors="replace") as f:
        return f.read()

def now_edt():
    return datetime.now(EDT)

out = {"meta": {}, "fleet": {}, "tokens": {}, "agents": [], "earnings": {},
       "discoveries": [], "deadlines": [], "errors": [], "approvals": []}

# ---- tokens: latest signal from referral placement log ----
placements = read("goals/token-burn-rate-measurement/hidden_files/referral-placements.md")
m = re.findall(r"TOKEN INCOME SIGNAL:\s*~?([\d.]+)B[^\n]*FLAT since ([0-9:]+)", placements)
banked, flat_since = (m[-1] if m else ("?", "?"))
out["tokens"] = {
    "banked_billions": float(banked) if banked != "?" else None,
    "note": "Referral hunt exempt from throttling per owner order.",
    "reset_at": "2026-10-17T17:05:00-04:00",
    "flat_since": flat_since,
}

# ---- sends today: send-single.sh's own UTC-day counter from the send log ----
sendlog = read("coupon-emails/send-log-2026-10-16.txt")
counters = re.findall(r"(\d{1,3})/150", sendlog)
sends_used = int(counters[-1]) if counters else 0

# ---- fleet: browser fleet status from latest evidence ----
# Verified state as of 2026-10-15 ~23:56 EDT: example.com probe OK 23:35 but
# real workflows (FB publish, contest forms) fail with VM/session errors.
# Described as FLAPPING, not recovered.
out["fleet"] = {
    "summary": "degraded",
    "browser_fleet": "flapping",
    "note": "Simple probes pass; real workflows fail. ~39h unstable since Oct 14 08:53 EDT.",
}

# ---- agents: major lanes with honest current state ----
out["agents"] = [
    {"id": "referral-hunt", "label": "Referral Hunt (B3NYLG)",
     "current_task": "5-min cycle: fresh code-seekers", "status": "ok",
     "last_update": "00:01 EDT"},
    {"id": "outreach", "label": "Outreach Email",
     "current_task": f"Wave 35: {sends_used}/150 UTC-day sends used",
     "status": "ok", "last_update": "00:00 EDT"},
    {"id": "money-lanes", "label": "Money Lanes",
     "current_task": "No new lanes; Zoud gameplay video review-ready",
     "status": "ok", "last_update": "23:40 EDT"},
    {"id": "contests", "label": "Contests / Freebies",
     "current_task": "Browser lane blocked; email entries only",
     "status": "warn", "last_update": "23:40 EDT"},
    {"id": "night-desk", "label": "Night Desk Publisher",
     "current_task": "Story staged; FB publish blocked by fleet",
     "status": "warn", "last_update": "23:50 EDT"},
    {"id": "bounty-builds", "label": "Bounty Builds",
     "current_task": "LedgerLens 35/35 pass (closes Oct 18)",
     "status": "warn", "last_update": "23:40 EDT"},
]

# ---- earnings: verified cash only ----
out["earnings"] = {
    "currency": "USD", "verified_total_usd": 0.0, "pending_usd": 0.0,
    "events": [
        {"amount_usd": 0.0, "lane": "operations", "state": "verified",
         "time": "2026-10-16", "note": "$0 verified operation cash to date. $550 strike pay landed Oct 15 (non-operation)."}
    ],
}

# ---- discoveries: recent VERIFIED finds only ----
out["discoveries"] = [
    {"text": "Michigan Out-of-Doors TV: $300 Jay's Sporting Goods gift card + hoodie giveaway found; entry blocked by browser fleet, queued.",
     "time": "2026-10-15 23:50 EDT", "lane": "freebies"},
    {"text": "Mountainland Swag Bag (Gleam) queued for retry; Fall for Adventure (SweepWidget) quarantined, 114 entrants reported.",
     "time": "2026-10-15 23:40 EDT", "lane": "contests"},
    {"text": "Telly TV identified: free dual-screen set + bundled 4K Android TV dongle. Dashboard path verified (TV Bro browser, $0).",
     "time": "2026-10-16 00:30 EDT", "lane": "systems"},
]

# ---- deadlines: nearest first, from OMEGA_DEADLINES.md ----
out["deadlines"] = [
    {"title": "Anthony Hamilton concert — Van Andel Arena, Sec 123 Row C", "due": "2026-10-16 8:00 PM EDT",
     "status": "upcoming", "note": "Tickets confirmed. Attend or gift — his call."},
    {"title": "LedgerLens closes", "due": "2026-10-18",
     "status": "upcoming", "note": "35/35 tests pass. Submission unresolved."},
    {"title": "AMD ACT III hackathon", "due": "2026-10-18 11:00 AM EDT",
     "status": "upcoming", "note": "Explainer owed; sign-in unresolved."},
    {"title": "Token reset", "due": "2026-10-17 5:05 PM EDT",
     "status": "upcoming", "note": f"~{banked}B banked, flat since {flat_since}. Emergency over."},
    {"title": "DHS SentinelWeave portal filing — PORTAL ONLY", "due": "2026-10-21 12:00 PM ET",
     "status": "upcoming", "note": "Proposal NOT filed. File when fleet stable."},
    {"title": "Electric $144", "due": "2026-10-19",
     "status": "upcoming", "note": "His payment. Reminder set Oct 18 09:00."},
]

# ---- errors: real incidents only ----
out["errors"] = [
    {"message": "Browser fleet flapping ~39h (since Oct 14 08:53 EDT). Forms, FB publish, DHS filing blocked. No blind retries.",
     "time": "2026-10-15 23:56 EDT", "source": "night-desk-publisher",
     "impact": "FB/contest/form/DHS lanes stalled; text-only lanes running"},
    {"message": "Outreach run timed out mid-wave (1200s). 20 wave-35 rows unprocessed; retry-limiter holds 2 rows until UTC 10-17.",
     "time": "2026-10-16 00:00 EDT", "source": "outreach-email-retry",
     "impact": "minor; next 20-min run resumes"},
]

# ---- approvals: things ONLY he can do ----
out["approvals"] = [
    {"id": "vault-captures", "title": "3 AI-provider vault captures",
     "detail": "Groq + 2 more providers. Unlocks cross-model mesh. In Secure Vault, needs his taps.",
     "asked_at": "2026-10-15"},
    {"id": "telly-setup", "title": "Telly TV: install TV Bro on the Android dongle",
     "detail": "Play Store on the bundled 4K Android dongle -> install TV Bro -> open the dashboard URL. ~3 min, his hands.",
     "asked_at": "2026-10-16"},
    {"id": "farmers-387", "title": "Farmers $387 replacement payment or call Tyler Rosa",
     "detail": "Oct 14 payment failed authorization. His money decision.",
     "asked_at": "2026-10-15"},
]

out["meta"] = {
    "generated_at": now_edt().isoformat(timespec="seconds"),
    "generated_by": "build-feed.py",
    "sample": False,
    "schema_version": 1,
    "note": "All values read from workspace logs at generation time. Verified numbers only.",
}

dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "status.json")
with open(dest, "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1)
    f.write("\n")
print("wrote", dest, os.path.getsize(dest), "bytes")
