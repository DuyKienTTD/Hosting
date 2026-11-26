import type { Config } from "./config.js";

type Intent = "stop" | "review" | "none";

function normalize(text: string) {
  return text.normalize("NFC").toLocaleLowerCase("vi-VN")
    // Keep "dùng" (use) distinct from "dừng" (stop).
    .replace(/(?<!\p{L})dùng(?!\p{L})/gu, "su dung")
    .normalize("NFD").replace(/\p{M}/gu, "").replace(/đ/gu, "d")
    .replace(/[^\p{L}\p{N}]+/gu, " ").trim()
    .replace(/\b(?:ko|k)\b/gu, "khong").replace(/\b(?:qc)\b/gu, "quang cao")
    .replace(/\b(?:km)\b/gu, "khuyen mai").replace(/\b(?:nt|tn)\b/gu, "tin nhan");
}

const refusal = /\b(?:ngung|dung|thoi|khoi|go|bo|xoa|huy|rut|loai|bot|cat|dep|tranh|du roi|stop|unsubscribe|khong|chang|chua|tu choi|mien)\b/u;
const marketing = /\b(?:quang cao|khuyen mai|uu dai|danh sach (?:nhan|gui) (?:tin|quang cao|uu dai|khuyen mai)|spam|lam phien|tiep thi|ban tin|newsletter|tin moi mua|chuong trinh)\b/u;
const continuation = /\b(?:dung (?:ngung|dung|thoi)|khong (?:muon |can )?(?:ngung|dung)|van muon (?:nhan|xem|doc))\b/u;
const deliveryProblem = /\b(?:(?:khong|chua) (?:nhan duoc|thay|gui duoc)|gui nham)\b/u;
const specific = /\b(?:xac nhan|dau cham|nham|tin (?:nay|do|tren|cu)|bao gia|hoa don|don hang|gui hang|nhan hang|giao hang|san pham|mau|mua|dat hang|thanh toan|bao hanh|kiem tra gia|su dung|dung (?:thu|tich|luong|cu|may))\b/u;
const question = /\b(?:tai sao|vi sao|the nao|lam sao|khi nao|co phai|la gi|co nen|vi du|cho toi biet|muon biet|giai thich|co nghia|trich dan|hoi cach|hoi ve|chua muon)\b/u;
const clearVerb = /\b(?:ngung|dung|huy|khong (?:muon |can )?nhan)\b/gu;
const clearObject = /\b(?:tin(?: nhan)?|quang cao|khuyen mai|uu dai|ban tin|spam|tiep thi)\b/gu;
const removal = /\b(?:go|xoa|bo|rut|loai)\b/gu;
const list = /\bkhoi danh sach\b/gu;

function follows(clause: string, verbs: RegExp, objects: RegExp, maxGap: number) {
  const targets = [...clause.matchAll(objects)];
  return [...clause.matchAll(verbs)].some(verb => {
    const start = verb.index!;
    if (/\b(?:khong|chua|chang|dung nhu) $/u.test(clause.slice(0, start))) return false;
    const end = start + verb[0].length;
    return targets.some(object => object.index! >= end &&
      (clause.slice(end, object.index!).match(/\S+/gu)?.length ?? 0) <= maxGap);
  });
}

export function classifyOptOut(text: string, config: Config["advertising"]): Intent {
  const normalized = normalize(text);
  if (config.optOutWords.includes(normalized) || normalized === "dung nhan tin") return "stop";
  let review = false;
  for (const sentence of text.match(/[^.!?;\n…]+[.!?;…]*/gu) ?? []) {
    const text = normalize(sentence);
    if (!marketing.test(text) || continuation.test(text) || deliveryProblem.test(text)) continue;
    review ||= refusal.test(text);
    if (sentence.includes("?") || question.test(text)) continue;
    for (const part of sentence.split(/,/u)) {
      for (const clause of normalize(part).split(/\b(?:roi|vi|nhung|tuy nhien|sau do|ma)\b/u)) {
        const candidate = clause.trim();
        if (!marketing.test(candidate) || specific.test(candidate) || /\b(?:duoc|phai|hay) khong$/u.test(candidate)) continue;
        if (follows(candidate, clearVerb, clearObject, config.optOutMaxGapWords) ||
          follows(candidate, removal, list, config.optOutMaxGapWords)) return "stop";
      }
    }
  }
  return review ? "review" : "none";
}
