// DeadlineGuardian — JS port of src/triage.py (v2: identical categories,
// weighted signals, urgency rules, confidence, summary, days-until logic).
const CATEGORIES = {
  bill_due: [{ "amount due": 2, "payment due": 2, "balance due": 2, "water bill": 2, bill: 1, utility: 1, electric: 1 },
    "Pay or schedule payment before the due date; if you cannot, call the biller before the due date to ask about a payment plan."],
  court_legal: [{ summons: 2, hearing: 2, "case no": 2, court: 1, probation: 1, judge: 1 },
    "Calendar the date immediately and keep the original; do not miss a court date — call the clerk if anything is unclear."],
  benefits: [{ redetermination: 2, "renewal notice": 2, "food assistance": 2, snap: 1, wic: 1, medicaid: 1, benefits: 1 },
    "Complete any requested verification before the deadline in the notice; missing it can stop benefits."],
  school_childcare: [{ immunization: 2, daycare: 1, childcare: 1, school: 1, enrollment: 1 },
    "Return the form / complete enrollment by the stated date and keep a copy."],
  medical: [{ prescription: 2, "lab results": 2, appointment: 1, clinic: 1, referral: 1 },
    "Confirm the appointment; add it to the calendar with travel time."],
  housing: [{ "land contract": 2, eviction: 2, lease: 1, rent: 1, mortgage: 1, landlord: 1 },
    "Note the due date; keep proof of every payment; respond in writing to any notice."],
  vehicle: [{ "license plate": 2, "auto insurance": 2, "secretary of state": 2, registration: 1, "insurance policy": 1, dmv: 1 },
    "Renew / respond before the expiration date to avoid late fees."],
  tax: [{ "property tax": 2, "tax notice": 2, treasurer: 2, irs: 1, assessment: 1 },
    "Calendar the tax due date; taxes are not covered by most assistance — plan the payment early."],
};
const GENERAL_ACTION = "File it, note any date in it, and check whether a reply is requested.";
const LABELS = { bill_due: "Bill due", court_legal: "Court / legal", benefits: "Benefits",
  school_childcare: "School / childcare", medical: "Medical", housing: "Housing",
  vehicle: "Vehicle", tax: "Tax", general_notice: "General notice" };
const DATE_RE = /\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\b|\b\d{1,2}\/\d{1,2}\/\d{2,4}\b/gi;
const AMOUNT_RE = /\$\s?([\d,]+\.\d{2}|[\d,]+)/g;
const URGENT_WORDS = ["final notice", "past due", "overdue", "shutoff", "disconnect", "eviction", "deadline", "immediately", "urgent"];
const MONTHS = { jan: 0, feb: 1, mar: 2, apr: 3, may: 4, jun: 5, jul: 6, aug: 7, sep: 8, oct: 9, nov: 10, dec: 11 };

function parseDate(s) {
  s = s.trim().replace(/,/g, " ").replace(/(\d)(st|nd|rd|th)\b/i, "$1").replace(/\s+/g, " ");
  let m = s.match(/^([a-z]+)\s+(\d{1,2})\s+(\d{4})$/i);
  if (m) {
    const mon = MONTHS[m[1].slice(0, 3).toLowerCase()];
    if (mon === undefined) return null;
    return new Date(Date.UTC(+m[3], mon, +m[2]));
  }
  m = s.match(/^(\d{1,2})\/(\d{1,2})\/(\d{2,4})$/);
  if (m) {
    let y = +m[3]; if (y < 100) y += 2000;
    return new Date(Date.UTC(y, +m[1] - 1, +m[2]));
  }
  return null;
}

function classify(text, todayISO) {
  const low = text.toLowerCase();
  let best = "general_notice", bestScore = 0, bestAction = GENERAL_ACTION, bestSignals = [];
  let totalWeight = 0;
  for (const [cat, [signals, action]] of Object.entries(CATEGORIES)) {
    const hits = Object.keys(signals).filter(k => low.includes(k));
    const score = hits.reduce((a, k) => a + signals[k], 0);
    totalWeight += score;
    if (score > bestScore) { best = cat; bestScore = score; bestAction = action; bestSignals = hits; }
  }
  const due_dates = text.match(DATE_RE) || [];
  const amounts = [...text.matchAll(AMOUNT_RE)].map(m => m[1]);
  const today = todayISO ? new Date(todayISO + "T00:00:00Z") : (() => { const n = new Date(); return new Date(Date.UTC(n.getFullYear(), n.getMonth(), n.getDate())); })();
  const parsed = due_dates.map(parseDate).filter(d => d !== null);
  const days_until = parsed.length ? Math.min(...parsed.map(d => Math.round((d - today) / 86400000))) : null;
  const urgentHit = URGENT_WORDS.some(w => low.includes(w));
  const urgency = (urgentHit || (days_until !== null && days_until <= 7)) ? "high" : (due_dates.length ? "medium" : "low");
  let confidence;
  if (best === "general_notice") confidence = (!due_dates.length && !amounts.length) ? 0.35 : 0.5;
  else {
    const share = totalWeight ? bestScore / totalWeight : 0;
    confidence = Math.round(Math.min(0.99, 0.45 + 0.3 * share + 0.05 * bestSignals.length) * 100) / 100;
  }
  let recommended_window;
  if (urgency === "high") recommended_window = "Act today — this is time-critical.";
  else if (days_until !== null && days_until <= 30) recommended_window = `Act within the next ${Math.max(days_until, 0)} days, before the due date.`;
  else if (due_dates.length) recommended_window = "Calendar it now and act well before the due date.";
  else recommended_window = "No date pressure found — file it and move on.";
  const bits = [LABELS[best]];
  if (amounts.length) bits.push("amount " + amounts.map(a => "$" + a).join(", "));
  if (due_dates.length) bits.push("due " + due_dates[0]);
  if (days_until !== null) bits.push(days_until < 0 ? "overdue" : days_until === 0 ? "due today" : `${days_until} day(s) left`);
  const summary = bits.join(" · ") + ` · urgency ${urgency}.`;
  return { category: best, urgency, due_dates, amounts, action: bestAction, score: bestScore,
    confidence, signals: bestSignals, summary, days_until, recommended_window };
}

function triageMany(texts, todayISO) {
  const rank = { high: 0, medium: 1, low: 2 };
  return texts.map(t => classify(t, todayISO)).sort((a, b) =>
    (rank[a.urgency] - rank[b.urgency]) ||
    ((a.days_until === null ? 1e9 : a.days_until) - (b.days_until === null ? 1e9 : b.days_until)));
}
function summarizeBatch(results) {
  const out = { total: results.length, high: 0, medium: 0, low: 0, by_category: {} };
  for (const r of results) { out[r.urgency]++; out.by_category[r.category] = (out.by_category[r.category] || 0) + 1; }
  return out;
}
if (typeof module !== "undefined") module.exports = { classify, triageMany, summarizeBatch, LABELS };
