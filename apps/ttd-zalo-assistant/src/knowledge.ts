import type { DatabaseSync } from "node:sqlite";

export type Source = {
  id: string; sku: string | null; kind: "product" | "price" | "policy" | "document";
  title: string; summary: string; version: string; effective: string; until: string | null;
  origin: string; amount: number | null; unit: string | null;
};

export function migrateKnowledge(db: DatabaseSync) {
  db.exec(`
    CREATE TABLE catalogue(id TEXT PRIMARY KEY, sku TEXT, kind TEXT NOT NULL, title TEXT NOT NULL,
      summary TEXT NOT NULL, version TEXT NOT NULL, effective TEXT NOT NULL, until TEXT,
      origin TEXT NOT NULL, amount INTEGER, unit TEXT);
    CREATE INDEX catalogue_sku ON catalogue(sku,kind,effective);
    CREATE VIRTUAL TABLE catalogue_fts USING fts5(id UNINDEXED, sku, title, summary, tokenize='unicode61 remove_diacritics 2');
    CREATE TRIGGER catalogue_insert AFTER INSERT ON catalogue BEGIN
      INSERT INTO catalogue_fts(rowid,id,sku,title,summary) VALUES(new.rowid,new.id,new.sku,new.title,new.summary);
    END;
    INSERT INTO catalogue
      SELECT id,id,'product',title,summary,'1','1970-01-01',NULL,id,NULL,NULL FROM knowledge;
  `);
}

const skuPattern = /^[A-Z0-9_-]{1,40}$/;
const datePattern = /^\d{4}-\d{2}-\d{2}$/;
export function validDate(date: string) {
  return typeof date === "string" && datePattern.test(date) &&
    !Number.isNaN(Date.parse(date)) && new Date(date).toISOString().slice(0, 10) === date;
}
export function localDate(now = new Date()) {
  return new Intl.DateTimeFormat("sv-SE", { timeZone: "Asia/Ho_Chi_Minh" }).format(now);
}

export class Knowledge {
  constructor(private readonly db: { prepare(sql: string): {
    all(...values: (string | number | null)[]): unknown[];
    run(...values: (string | number | null)[]): unknown;
  } }, private readonly backend?: "postgres") {}

  add(row: Source) {
    if (![row.id, row.title, row.summary, row.version, row.origin].every(
      (field) => typeof field === "string" && field.trim() && field.length <= 12000) ||
      !validDate(row.effective) || (row.until !== null && (!validDate(row.until) || row.until <= row.effective)) ||
      !["product", "price", "policy", "document"].includes(row.kind) ||
      ((row.kind === "price" || row.kind === "product") && (typeof row.sku !== "string" || !skuPattern.test(row.sku))) ||
      (row.sku !== null && (typeof row.sku !== "string" || !skuPattern.test(row.sku))) ||
      (row.amount !== null && (row.kind !== "price" || !Number.isSafeInteger(row.amount) || row.amount < 0)) ||
      (row.kind === "price" && (typeof row.unit !== "string" || !/^[\p{L} ]{1,30}$/u.test(row.unit))) ||
      (row.kind !== "price" && row.unit !== null)) throw Error("INVALID_CATALOGUE");
    this.db.prepare("INSERT INTO catalogue VALUES(?,?,?,?,?,?,?,?,?,?,?)").run(
      row.id, row.sku, row.kind, row.title, row.summary, row.version, row.effective, row.until, row.origin, row.amount, row.unit);
    return row.id;
  }

  import(text: string, filename?: string) {
    if (typeof text !== "string" || !text.trim() || text.length > 12000) throw Error("INVALID_DOCUMENT");
    const legacy = /^SKU: ([A-Z0-9_-]{1,40})\r?\nTên: ([^\r\n]{1,120})\r?\nThông tin: ([^\r\n]{1,2000})\r?\n?$/u.exec(text);
    if (filename === undefined && legacy) {
      const [, id, title, summary] = legacy;
      return this.add({ id, sku: id, title, summary, kind: "product", version: "1",
        effective: "1970-01-01", until: null, origin: id, amount: null, unit: null });
    }
    if (typeof filename !== "string" || filename.length > 120 || !/^[^/\\\x00-\x1f]+\.(?:txt|md)$/i.test(filename)) {
      throw Error("INVALID_DOCUMENT");
    }
    return this.add({ id: crypto.randomUUID(), sku: null, kind: "document", title: filename,
      summary: text, version: "1", effective: localDate(), until: null, origin: filename, amount: null, unit: null });
  }

  search(query = "", sku?: string) {
    if (typeof query !== "string" || query.length > 100 ||
        (sku !== undefined && (typeof sku !== "string" || !skuPattern.test(sku)))) throw Error("INVALID_QUERY");
    const terms = query.normalize("NFC").match(/[\p{L}\p{N}]+/gu)?.map((term) => `"${term}"`).join(" AND ");
    const filter = sku ?? (skuPattern.test(query.toUpperCase()) && this.bySku(query.toUpperCase()).length ? query.toUpperCase() : null);
    if (terms && filter !== query.toUpperCase()) {
      if (this.backend === "postgres") return this.db.prepare(`SELECT c.* FROM catalogue c
        WHERE to_tsvector('simple',concat_ws(' ',sku,title,summary)) @@ websearch_to_tsquery('simple',?)
          AND (? IS NULL OR c.sku=?) ORDER BY c.id LIMIT 100`).all(terms.replaceAll(" AND ", " "), filter, filter) as Source[];
      return this.db.prepare(`SELECT c.* FROM catalogue_fts f JOIN catalogue c ON c.rowid=f.rowid
        WHERE catalogue_fts MATCH ? AND (? IS NULL OR c.sku=?) ORDER BY bm25(catalogue_fts),c.id LIMIT 100`)
        .all(terms, filter, filter) as Source[];
    }
    if (query.trim() && !terms) return [];
    return this.db.prepare("SELECT * FROM catalogue WHERE ? IS NULL OR sku=? ORDER BY id LIMIT 100")
      .all(filter, filter) as Source[];
  }

  findDocuments(question: string, date: string, sku?: string) {
    const words = question.normalize("NFC").toLocaleLowerCase("vi-VN").match(/[\p{L}\p{N}]+/gu) ?? [];
    const stop = new Set("cho tôi em mình anh chị bạn biết hỏi về là gì có không được như thế nào xin vui lòng giúp nhé ạ quy trình".split(" "));
    const terms = words.filter(word => !stop.has(word) && !/^\d+$/u.test(word)).slice(0, 24);
    const phrases = [...new Set(terms.slice(1).map((word, i) => `"${terms[i]} ${word}"`))];
    if (!phrases.length) return [];
    if (this.backend === "postgres") return this.db.prepare(`SELECT c.* FROM catalogue c
      WHERE to_tsvector('simple',concat_ws(' ',sku,title,summary)) @@ websearch_to_tsquery('simple',?)
        AND c.kind='document' AND (c.sku IS NULL OR c.sku=?)
        AND c.effective<=? AND (c.until IS NULL OR c.until>?)
      ORDER BY c.id LIMIT 3`).all(phrases.join(" OR "), sku ?? null, date, date) as Source[];
    return this.db.prepare(`SELECT c.* FROM catalogue_fts f JOIN catalogue c ON c.rowid=f.rowid
      WHERE catalogue_fts MATCH ? AND c.kind='document' AND (c.sku IS NULL OR c.sku=?)
        AND c.effective<=? AND (c.until IS NULL OR c.until>?)
      ORDER BY bm25(catalogue_fts),c.id LIMIT 3`).all(phrases.join(" OR "), sku ?? null, date, date) as Source[];
  }

  bySku(sku: string) {
    return this.db.prepare("SELECT * FROM catalogue WHERE sku=? ORDER BY id").all(sku) as Source[];
  }

  policies() {
    return this.db.prepare("SELECT * FROM catalogue WHERE kind='policy' ORDER BY id").all() as Source[];
  }
}
