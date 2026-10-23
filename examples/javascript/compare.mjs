// Compare two AsOf passports question by question (Node 18+ or any browser).
//   node compare.mjs paxg xaut
// Shows what each issuer's documents say side by side, with the evidence label.
// No ranking, no score. Data: CC BY 4.0, "AsOf by Diikun LAB".

const BASE = process.env.ASOF_BASE ?? "https://asof.diikunapp.workers.dev"; // moving to https://asof.pro
const LAYERS = ["summary", "legal", "exit", "backing", "rules"];

const get = async (id) => {
  const r = await fetch(`${BASE}/api/v1/passports/${id}.json`);
  if (!r.ok) throw new Error(`${id}: HTTP ${r.status}`);
  return r.json();
};

const answer = (p, field) => {
  const f = p.facts.find((x) => x.field === field);
  return f ? `${f.text} [${f.evidence}]` : "Unknown";
};

const [a, b] = await Promise.all([get(process.argv[2] ?? "paxg"), get(process.argv[3] ?? "xaut")]);

const fields = new Map();
for (const p of [a, b]) for (const x of [...p.facts, ...p.unknowns]) fields.set(x.field, LAYERS.indexOf(x.layer));

const rows = [...fields].sort((x, y) => x[1] - y[1]).map(([field]) => ({
  field,
  [`${a.ticker} (as of ${a.as_of.slice(0, 10)})`]: answer(a, field),
  [`${b.ticker} (as of ${b.as_of.slice(0, 10)})`]: answer(b, field),
}));
console.table(rows);
console.log(`Source: AsOf by Diikun LAB — CC BY 4.0. Not investment advice.`);
