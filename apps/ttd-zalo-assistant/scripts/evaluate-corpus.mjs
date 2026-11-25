import { execFileSync } from "node:child_process";
import { Foundation } from "../dist/foundation.js";
import { FakeProvider } from "../dist/ai.js";

const ref = "3dfc6fa1a0140267ac8d5604a5169299bd62b68d";
const file = name => JSON.parse(execFileSync("git", [
  "show", `${ref}:program/zalo-mvp01/zpc-03-corpus/${name}.json`,
], { encoding: "utf8" }));
const { cases, version } = file("cases");
const fixtures = file("customer-context");
const knowledge = file("knowledge");
const enabled = { retain: true, respond: true, send: false };
const denied = { retain: false, respond: false, send: false };
const targets = { "cust-A": "customer-a", "cust-B": "customer-b", "cust-C": "customer-a" };

function loadKnowledge(db) {
  const add = (group, row, data) => db.addCatalogueSource({
    id: row.id, sku: row.sku ?? null, version: group.version ?? "1.0", effective: group.effective_from,
    until: group.effective_to_exclusive ?? null, amount: null, unit: null,
    origin: `knowledge.json#${row.id}`, ...data,
  });
  for (const row of knowledge.products.rows) {
    const weight = row.weight_g === null ? "chưa có" : `${(row.weight_g / 1000).toLocaleString("vi-VN")} kg`;
    add(knowledge.products, row, { kind: "product", title: row.title, summary:
      `Cao ${row.height_cm} cm, ngang ${row.width_cm} cm và sâu ${row.depth_cm} cm. Khối lượng: ${weight}. Vật liệu: ${row.material}. Đặt tối thiểu ${row.min_order} ${row.order_unit}.` });
  }
  for (const book of knowledge.price_books) for (const row of book.rows) {
    add(book, row, { kind: "price", title: "Bảng giá mẫu " + book.version, summary: "Giá mẫu",
      amount: row.amount_vnd, unit: row.unit });
  }
  for (const row of knowledge.policies.rows) {
    add(knowledge.policies, row, { kind: "policy", title: row.topic, summary: row.text });
  }
  for (const row of knowledge.untrusted_documents.rows) {
    add(knowledge.untrusted_documents, row, { kind: "document", title: row.id, summary: row.text });
  }
}

// Check the main factual anchors independently of the non-binding reference wording.
const anchors = {
  "001": /123\.456 VND\/chiếc/, "002": /1\.664\.000.*208\.000/, "003": /247\.000 VND\/chiếc/,
  "004": /2\.976\.000/, "013": /100 cm.*1,4 kg/, "014": /thép đặc giả định.*16 chiếc/,
  "015": /2 mét.*kiểm tra khối lượng/, "016": /ngang 7 cm và sâu 7 cm/,
  "017": /ngày thứ 7/, "018": /đã lắp.*không thuộc/, "019": /đặt riêng.*không thuộc/,
  "021": /12 tháng/, "022": /[Tt]rầy xước do lắp đặt không thuộc/,
  "023": /13 tháng đã quá/, "025": /REF-MOCK-A/, "026": /REF-MOCK-B/,
  "029": /123\.456 VND\/chiếc/, "030": /1,5 kg/, "031": /100 cm/, "038": /REF-MOCK-A/,
  "040": /7 ngày[\s\S]*12 tháng/, "048": /88 cm/,
};
let passed = 0;
for (const item of cases) {
  const context = item.customer_context;
  const target = targets[context.customer_id];
  let calls = 0;
  const adapter = new FakeProvider();
  const db = new Foundation(":memory:", { draft(input) { calls++; return adapter.draft(input); } }, () => context.as_of);
  const sourceAliases = new Map();
  try {
    loadKnowledge(db);
    db.setStopped(false);
    const makeConsent = (id, consent) => db.setConsent(id, consent, Date.now() + 60_000, false);
    const customers = context.customer_id === "cust-C" ?
      fixtures.customers.filter(row => row.customer_id === "cust-C") : fixtures.customers.slice(0, 2);
    for (const customer of customers) {
      const id = targets[customer.customer_id];
      makeConsent(id, customer.consent);
      for (const memory of customer.memory) {
        const { id: source } = db.receive(id, memory.id, memory.text);
        db.remember(id, source, memory.text);
        sourceAliases.set(source, memory.id);
      }
    }
    if (target) for (const [i, turn] of context.prior_turns.entries()) {
      db.receive(target, "prior-" + i, turn.text);
    }
    const control = context.control;
    if (control.consent_revoked_at) makeConsent(target, { ...enabled, send: true });
    if (control.stop) db.setStopped(true);
    if (control.consent_revoked_before_draft) makeConsent(target, denied);
    let draft;
    let usableDrafts = 0;
    let newWrites = 0;
    if (target) {
      const origin = db.receive(target, item.id, item.input);
      newWrites = Number(origin.state === "retained");
      if (origin.canDraft) {
        draft = db.draft(target, origin.id);
        usableDrafts = Number(draft.action !== "từ chối");
        if (control.consent_revoked_at) {
          const grant = db.approve(target, draft.text, origin.id);
          makeConsent(target, denied);
          try { await db.send(grant, target, draft.text); }
          catch (error) {
            if (!/SEND_REVOKED|APPROVAL_MISMATCH/.test(error.message)) throw error;
            draft = undefined;
            usableDrafts = 0;
          }
        }
      }
    }
    const observed = {
      action: draft?.action ?? (target ? "từ chối" : "hỏi lại"),
      sources: (draft?.sourceIds ?? []).map(id => sourceAliases.get(id) ?? id).sort(),
      effects: { schedule_count: 0, send_count: db.status().fakeSends,
        suggest_operator_follow_up: draft?.suggestFollowUp ?? false, draft_count: Number(!!draft),
        model_dispatch_count: calls, usable_draft_count: usableDrafts, new_customer_content_write_count: newWrites },
    };
    const expected = item.expected;
    const anchor = anchors[item.id.slice(-3)];
    const valid = observed.action === expected.action &&
      JSON.stringify(observed.sources) === JSON.stringify([...expected.source_ids].sort()) &&
      Object.entries(expected.effects).every(([key, value]) => observed.effects[key] === value) &&
      (!anchor || anchor.test(draft?.text ?? "")) &&
      !(expected.action === "hỏi lại" && /^gia_/u.test(item.category) && /\d[\d.]*\s+VND/u.test(draft?.text ?? ""));
    if (valid) passed++;
    else console.log(item.id, observed.action, observed.sources.join(","), draft?.text ?? "[không có nháp]");
  } finally {
    db.close();
  }
}
console.log(`ZPC-03 v${version}: ${passed}/${cases.length} match action, sources, effects and selected factual anchors.`);
if (passed !== cases.length) process.exitCode = 1;
