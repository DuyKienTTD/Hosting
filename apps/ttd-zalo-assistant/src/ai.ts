import { validDate, type Source } from "./knowledge.js";

type Action = "trả lời" | "hỏi lại" | "chuyển người vận hành" | "đề xuất follow-up" | "từ chối";
export type Draft = {
  action: Action; text: string; sourceIds: string[];
  suggestFollowUp: boolean; confidence: "grounded" | "uncertain"; source: { id: string; title: string } | null;
};
export type AIInput = {
  question: string; date: string; sources: readonly Source[]; sku?: string; memory?: readonly MemoryEvidence[];
};
export type MemoryEvidence = {
  id: string; type: "sku" | "reference"; value: string;
};
export interface AIAdapter {
  draft(input: Readonly<AIInput>): Draft;
}

function result(action: Action, text: string, sources: readonly Pick<Source, "id" | "title">[] = [], suggestFollowUp = false): Draft {
  const [first] = sources;
  return { action, text, suggestFollowUp, sourceIds: sources.map(row => row.id), confidence: action === "trả lời" ? "grounded" : "uncertain",
    source: action === "trả lời" && first ? { id: first.id, title: first.title } : null };
}

export function extractSkus(question: string) {
  const explicit = [...question.matchAll(/\bSKU[ :]+([A-Z0-9_-]{1,40})(?![A-Z0-9_-])/gi)].map(m => m[1].toUpperCase());
  const codes = [...question.matchAll(/(?<![A-Z0-9_-])(?:[A-Z][A-Z0-9_]*-[A-Z0-9_-]*\d[A-Z0-9_-]*|R\d{2})(?![A-Z0-9_-])/gi)]
    .map(m => /^R\d{2}$/i.test(m[0]) ? "SYN-RAIL-" + m[0].slice(1) : m[0].toUpperCase());
  return [...new Set([...explicit, ...codes])];
}

export function questionDate(question: string, fallback: string) {
  if (/đổi|bảo hành|nhận hàng/iu.test(question)) return fallback;
  const date = /\b(?:ngày|sáng)\s+(\d{1,2})\/(\d{1,2})(?:\/(\d{4}))?/iu.exec(question);
  if (!date) return fallback;
  return `${date[3] ?? fallback.slice(0, 4)}-${date[2].padStart(2, "0")}-${date[1].padStart(2, "0")}`;
}

export const asksReference = (text: string) => /mã.*(?:tham chiếu|đơn).*lưu|lưu mã tham chiếu|nhắc lại mã đơn/iu.test(text);

const explicitPrice = /(?<![\p{L}])(?:giá|price|hết nhiêu|chiếc tính sao|bảng mới)(?![\p{L}])/iu;
const specification = /(?<![\p{L}])(?:cao|nặng|tối thiểu|kích thước|khối lượng|chiều (?:cao|rộng|dài|sâu)|vật liệu|chất liệu|làm bằng)(?![\p{L}])/iu;

function productDetails(product?: Source) {
  if (!product || /giá\s*[:=]|\bVND\b|\bUSD\b/iu.test(product.summary)) return undefined;
  return product.title + ": " + product.summary;
}

export class FakeProvider implements AIAdapter {
  draft({ question, date, sources, sku, memory = [] }: AIInput) {
    if (/khách (?:còn lại|khác)|thời tiết|tạo đơn|thu tiền|cước|chắc chắn giao/iu.test(question)) {
      return result("từ chối", "Yêu cầu này cần người vận hành kiểm tra đúng phạm vi và nguồn.");
    }
    if (asksReference(question)) {
      const ref = memory.find(row => row.type === "reference");
      return ref ? result("trả lời", `Mã tham chiếu đã lưu là ${ref.value}.`, [{ id: ref.id, title: "Tin nhắn nguồn" }]) :
        result("hỏi lại", "Bạn vui lòng xác nhận phiên và mã tham chiếu của mình.");
    }
    const products = sources.filter(row => row.kind === "product" && row.sku === sku);
    if (/chịu.*tải|chứng nhận/iu.test(question)) {
      return result("từ chối", "Catalogue chưa xác nhận tải trọng. Bạn có thể đề nghị người phụ trách cung cấp tài liệu kỹ thuật.", products);
    }
    const policies = sources.filter(row => row.kind === "policy");
    const follow = policies.find(row => /theo dõi/iu.test(row.title));
    const skuFact = memory.find(row => row.type === "sku");
    const scope = skuFact ? [{ id: skuFact.id, title: "Tin nhắn nguồn" }] : [];
    const wantsSpecification = specification.test(question);
    const wantsPrice = explicitPrice.test(question) || (!wantsSpecification && /bao nhiêu/iu.test(question));
    if (wantsPrice) {
      const product = wantsSpecification && products.length === 1 ? products[0] : undefined;
      const details = productDetails(product);
      const priceReply = (action: Action, text: string, evidence: readonly Pick<Source, "id" | "title">[],
        suggestFollowUp = false) => {
        if (!wantsSpecification) return result(action, text, evidence, suggestFollowUp);
        const missingWeight = /nặng|khối lượng/iu.test(question) && /khối lượng: chưa có/iu.test(details ?? "");
        const specificationReply = details ?? "Thông số bạn hỏi cần được xác minh thêm.";
        return result(action === "trả lời" && details && !missingWeight ? action : "hỏi lại",
          specificationReply + " " + text, [...new Map([
            ...scope, ...evidence, ...(details && product ? [product] : []),
          ].map(row => [row.id, row])).values()]);
      };
      const prices = sources.filter(row => row.kind === "price" && row.sku === sku);
      const [price] = prices;
      if (follow && sku && /kiểm tra.*giá/iu.test(question) && /báo em|đừng chủ động|^vâng/iu.test(question)) {
        const suggest = !/đừng chủ động/iu.test(question);
        return priceReply("trả lời", suggest ? `Có thể đề xuất người phụ trách xác minh giá ${sku}. Thời điểm phản hồi còn chờ xác nhận.` :
          `Giá ${sku} cần xác minh. Bạn có thể hỏi lại trong phiên này khi thuận tiện.`, [follow, ...prices], suggest);
      }
      if (!price || price.amount === null || prices.some(row => row.amount !== price.amount || row.unit !== price.unit)) {
        return priceReply("hỏi lại", "Chưa xác minh được giá hiện hành. Bạn vui lòng xác nhận mã và số lượng để nhân viên kiểm tra.", prices);
      }
      const priceQuestion = wantsSpecification ?
        question.split(/[,;?\n]|\s+(?:và|còn)\s+/iu).filter(part => explicitPrice.test(part)).join(" ") : question;
      const quantity = /(?<![\d.,])\b([1-9]\d{0,5})\s+(chiếc|mét)\b/iu.exec(priceQuestion);
      if (quantity && quantity[2].toLowerCase() !== price.unit) {
        return priceReply("hỏi lại", "Bạn vui lòng xác nhận đơn vị để nhân viên đối chiếu bảng giá.", prices);
      }
      const amount = price.amount.toLocaleString("vi-VN");
      if (quantity && Number(quantity[1]) > 1 && quantity[2].toLowerCase() === price.unit &&
          Number.isSafeInteger(price.amount * Number(quantity[1])) && products.length === 1) {
        return priceReply("trả lời", `${quantity[1]} ${quantity[2]} ${sku} là ${(price.amount * Number(quantity[1])).toLocaleString("vi-VN")} VND theo đơn giá ${amount} VND/${price.unit}.`, [...scope, ...prices, ...products]);
      }
      return priceReply("trả lời", `${sku} có giá ${amount} VND/${price.unit}.`, [...scope, ...prices]);
    }
    const topics = policies.filter(row => (/đổi|trả hàng/iu.test(question) && /đổi trả/iu.test(row.title)) ||
      (/bảo hành/iu.test(question) && /bảo hành/iu.test(row.title)));
    if (topics.length && new Set(topics.map(row => row.title)).size === topics.length) {
      const [topic] = topics;
      const months = /sau (\d+) tháng/iu.exec(question);
      const limit = /(\d+) tháng/iu.exec(topic.summary);
      if (topics.length === 1 && /bảo hành/iu.test(topic.title) && months && limit && Number(months[1]) > Number(limit[1])) {
        return result("trả lời", `Thời hạn theo chính sách là ${limit[1]} tháng. Mốc ${months[1]} tháng đã quá thời hạn đó.`, topics);
      }
      if (topics.length === 1 && /đổi trả/iu.test(topic.title) && /đã lắp|lắp bộ rồi|đặt riêng/iu.test(question) &&
          /đã lắp.*đặt riêng.*không thuộc/iu.test(topic.summary)) {
        return result("trả lời", "Theo chính sách, hàng đã lắp hoặc đặt riêng không thuộc diện đổi.", topics);
      }
      const dates = [...question.matchAll(/(?:ngày )?(\d{1,2})\/(\d{1,2})/gu)];
      const returnDays = /(\d+) ngày lịch/iu.exec(topic.summary);
      if (topics.length === 1 && /đổi trả/iu.test(topic.title) && dates.length === 2 && returnDays &&
          /chưa lắp/iu.test(question) && /(?:đủ phụ kiện|nguyên hộp)/iu.test(question) && /REF-[A-Z0-9-]+/iu.test(question)) {
        const [first, second] = dates;
        const year = Number(date.slice(0, 4));
        const received = Date.UTC(year, Number(first[2]) - 1, Number(first[1]));
        const requested = Date.UTC(year + Number(Number(second[2]) < Number(first[2])), Number(second[2]) - 1, Number(second[1]));
        const days = (requested - received) / 86_400_000;
        if (days >= 0 && days <= Number(returnDays[1])) {
          return result("trả lời", `Yêu cầu vào ngày thứ ${days} sau khi nhận, trong thời hạn ${returnDays[1]} ngày. Người phụ trách có thể xem xét theo tình trạng bạn cung cấp.`, topics);
        }
      }
      const needsDetails = /cần đưa gì|bị bong/iu.test(question);
      return result(needsDetails ? "hỏi lại" : "trả lời", needsDetails ?
        "Bạn vui lòng cung cấp mã tham chiếu, ngày nhận và tình trạng sản phẩm để đối chiếu chính sách." :
        topics.map(row => row.summary).join("\n"), topics);
    }
    if (follow && /theo dõi/iu.test(question)) {
      return result("hỏi lại", "Bạn muốn người phụ trách theo dõi việc gì?", [follow]);
    }
    const details = productDetails(products.length === 1 ? products[0] : undefined);
    if (details) {
      const product = products[0];
      if (/nặng|khối lượng/iu.test(question) && /khối lượng: chưa có/iu.test(product.summary)) {
        return result("hỏi lại", product.summary + " Bạn có muốn người phụ trách kiểm tra khối lượng?", [product]);
      }
      return result("trả lời", details, [...scope, product]);
    }
    const documents = sources.filter(row => row.kind === "document");
    if (documents.length) {
      return result("hỏi lại", "Có tài liệu tham khảo liên quan. Bạn muốn nhân viên đối chiếu nội dung nào trong tài liệu đã dẫn?", documents);
    }
    return result("hỏi lại", "Bạn vui lòng xác nhận mã sản phẩm và thông tin cần hỏi để tôi kiểm tra thêm.");
  }
}

export function validatedDraft(adapter: AIAdapter, input: AIInput): Draft {
  const sources = input.sources.filter(row => validDate(input.date) && row.effective <= input.date &&
    (!row.until || input.date < row.until) && (row.kind === "policy" || (row.kind === "document" && row.sku === null) || row.sku === input.sku));
  const memory = input.memory ?? [];
  const allowed = [...sources, ...memory.map(row => ({ id: row.id, title: "Tin nhắn nguồn" }))];
  const draft = adapter.draft({ question: input.question, date: input.date, sku: input.sku,
    sources: sources.map(row => row.kind === "document" ?
      { ...row, title: "Tài liệu tham khảo", summary: "", origin: "" } : { ...row }), memory: memory.map(row => ({ ...row })) });
  if (!draft || !["trả lời", "hỏi lại", "chuyển người vận hành", "đề xuất follow-up", "từ chối"].includes(draft.action) ||
      Object.keys(draft).some(key => !["action", "text", "sourceIds", "confidence", "source", "suggestFollowUp"].includes(key)) ||
      typeof draft.suggestFollowUp !== "boolean" ||
      (draft.suggestFollowUp && (draft.action !== "trả lời" || !sources.some(row =>
        draft.sourceIds?.includes(row.id) && row.kind === "policy" && /theo dõi/iu.test(row.title)))) ||
      typeof draft.text !== "string" || !draft.text.trim() || draft.text.length > 2000 ||
      !Array.isArray(draft.sourceIds) || new Set(draft.sourceIds).size !== draft.sourceIds.length ||
      draft.sourceIds.some(id => !allowed.some(row => row.id === id)) ||
      (draft.action === "trả lời" && !draft.sourceIds.length)) throw Error("INVALID_DRAFT");
  return result(draft.action, draft.text, draft.sourceIds.map(id => allowed.find(row => row.id === id)!), draft.suggestFollowUp);
}
