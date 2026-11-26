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

const stop = /\b(?:khong (?:muon|can|nhan|gui|nhan tin)|huy (?:dang ky|dk)|ngung|dung|thoi|khoi|go|bo|xoa|huy|rut|loai|stop|unsubscribe)\b/gu;
const messaging = /\b(?:tin nhan|nhan|tin|gui)\b/gu;
const marketing = /\b(?:quang cao|khuyen mai|uu dai|danh sach|spam|lam phien|tiep thi|ban tin)\b/gu;
const purchase = /\b(?:bao gia|hoa don|don hang|huy don|gui hang|nhan hang|giao hang|san pham|mua|dat hang|thanh toan|bao hanh|kiem tra gia)\b/u;
const inquiry = /\b(?:tai sao|vi sao|the nao|lam sao|co phai|la gi|co nen|giup toi hieu|vi du|cho toi biet|muon biet|giai thich|co nghia)\b/u;

function gap(sentence: string, verb: RegExpMatchArray, object: RegExpMatchArray) {
  const v = verb.index!;
  const o = object.index!;
  if (v + verb[0].length <= o) return sentence.slice(v + verb[0].length, o).trim().split(/\s+/u).filter(Boolean).length;
  if (o + object[0].length <= v) return sentence.slice(o + object[0].length, v).trim().split(/\s+/u).filter(Boolean).length;
  return 0; // "không nhận" already names the receive action.
}

export function classifyOptOut(text: string, config: Config["advertising"]): Intent {
  if (config.optOutWords.includes(normalize(text))) return "stop";
  let unsure = false;
  for (const raw of text.match(/[^.!?;\n…]+[.!?;…]*/gu) ?? []) {
    const sentence = normalize(raw);
    if (!sentence || /\b(?:su dung|dung (?:thu|tich|luong|cu|may))\b/u.test(sentence)) continue;
    const verbs = [...sentence.matchAll(stop)].filter(match =>
      !/(?:^| )khong $/u.test(sentence.slice(0, match.index!)));
    if (!verbs.length) continue;

    const ads = [...sentence.matchAll(marketing)];
    const objects = [...sentence.matchAll(messaging), ...ads];
    const near = (matches: RegExpMatchArray[]) => verbs.some(verb =>
      matches.some(object => gap(sentence, verb, object) <= config.optOutMaxGapWords));
    if (inquiry.test(sentence) || raw.includes("?") || (/\b(?:duoc|phai|hay) khong$/u.test(sentence))) {
      unsure ||= objects.length > 0;
      continue;
    }
    if (purchase.test(sentence) && !near(ads.filter(object => object[0] !== "danh sach"))) continue;
    const explicitLegacy = /^(?:toi |minh |em )?(?:xin )?huy (?:dang ky|dk)(?: cam on)?$/u.test(sentence);
    if (near(objects) || explicitLegacy) return "stop";
    unsure = true;
  }
  return unsure ? "review" : "none";
}
