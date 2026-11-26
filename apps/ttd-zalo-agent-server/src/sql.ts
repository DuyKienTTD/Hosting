export type Parameter = null | string | number | bigint | Uint8Array;
export type Row = Record<string, Parameter>;
export interface Statement {
  get(...values: Parameter[]): Row | undefined;
  all(...values: Parameter[]): Row[];
  run(...values: Parameter[]): { changes: number | bigint };
}
export interface RuntimeDatabase {
  readonly backend?: "postgres";
  prepare(sql: string): Statement;
  exec(sql: string): void;
  close(): void;
}
