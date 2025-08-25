// sync.mjs — fetch Sheet CSV → normalize → write docs/entries.json
import { writeFile, mkdir } from "node:fs/promises";

function parseCSV(text) {
  const rows = [];
  let i = 0, cell = "", row = [], inQuotes = false;
  const pushCell = () => { row.push(cell); cell = ""; };
  const pushRow  = () => { rows.push(row); row = []; };

  while (i < text.length) {
    const c = text[i];
    if (inQuotes) {
      if (c === '"') {
        if (text[i + 1] === '"') { cell += '"'; i++; } else { inQuotes = false; }
      } else { cell += c; }
    } else {
      if (c === '"') inQuotes = true;
      else if (c === ',') pushCell();
      else if (c === '\n' || c === '\r') { if (c === '\r' && text[i + 1] === '\n') i++; pushCell(); pushRow(); }
      else { cell += c; }
    }
    i++;
  }
  pushCell(); pushRow();

  const headers = rows.shift().map(h => h.trim());
  return rows
    .filter(r => r.some(x => x && x.trim() !== ""))
    .map(r => Object.fromEntries(headers.map((h, idx) => [h, (r[idx] ?? "").trim()])));
}

function toGradeNumber(g) {
  const n = Number(String(g || "").replace(/[^\d]/g, ""));
  return Number.isFinite(n) ? n : null;
}

function normalizeRows(rows) {
  return {
    meta: {
      source: "Google Sheet CSV",
      generatedAt: new Date().toISOString(),
      count: rows.length
    },
    entries: rows.map(r => ({
      id: r.RowId,
      Grade: toGradeNumber(r.Grade),
      Subject: r.Subject,
      Concept: `${r.Strand} — ${r.Substrand}`,
      StudentQuestion: r.StudentQuestion,
      AIGuidedHint: r.GuidedHint,
      RelatedPrompt1: r.FollowUp1 || "",
      RelatedPrompt2: r.FollowUp2 || "",
      Difficulty: r.Difficulty || "Medium",
      Tags: r.Tags || "",
      _cbc: {
        level: r.CBC_Level,
        strand: r.Strand,
        substrand: r.Substrand,
        slo: r.SLO,
        ref: r.KICD_RefURL || "",
        pathway: r.Pathway || ""
      }
    }))
  };
}

async function main() {
  const url = process.env.CBC_SHEET_URL;
  if (!url) throw new Error("Missing CBC_SHEET_URL env");

  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error(`Fetch failed ${res.status}`);
  const csv = await res.text();
  const rows = parseCSV(csv);
  const json = normalizeRows(rows);

  await mkdir("docs", { recursive: true });
  await writeFile("docs/entries.json", JSON.stringify(json, null, 2), "utf8");
  await writeFile("docs/version.txt", `${json.meta.generatedAt}\n`, "utf8");

  console.log(`Wrote docs/entries.json (${json.entries.length} entries)`);
}

main().catch(err => { console.error(err); process.exit(1); });
