import { agents } from "../config.js";

export const targets = ["claude", ...agents] as const;
export type Target = typeof targets[number];
export function isTarget(value: unknown): value is Target {
  return targets.some(target => target === value);
}

type Schema = {
  type: "object" | "array" | "string";
  properties?: Record<string, Schema>;
  required?: string[];
  additionalProperties?: false;
  items?: Schema;
  maxItems?: number;
  minLength?: number;
  maxLength?: number;
  enum?: readonly string[];
  pattern?: string;
};

const string = (maxLength: number): Schema => ({ type: "string", minLength: 1, maxLength });
const object = (properties: Record<string, Schema>): Schema => ({
  type: "object", properties, required: Object.keys(properties), additionalProperties: false,
});
const array = (items: Schema, maxItems: number): Schema => ({ type: "array", items, maxItems });

const recordId = "[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}";
export const reference = new RegExp("^[a-z][a-z0-9_]{0,31}:" + recordId + "$", "u");
export const planSchema = object({
  tasks: array(object({ agent: { type: "string", enum: agents }, instruction: string(600) }), 3),
});
export const resultSchema = object({
  summary: string(1200),
  links: array({ ...string(70), pattern: reference.source }, 5),
  proposals: array(object({
    action: { type: "string", enum: ["customer.rename"] },
    customer: { ...string(70), pattern: "^customer:" + recordId + "$" },
    name: string(120),
  }), 3),
});
export const synthesisSchema = object({ summary: string(1200) });

export type Plan = { tasks: { agent: typeof agents[number]; instruction: string }[] };
export type Result = { summary: string; links: string[]; proposals: { action: "customer.rename"; customer: string; name: string }[] };
export type Synthesis = { summary: string };

export function matches(schema: Schema, value: unknown): boolean {
  if (schema.type === "string") {
    return typeof value === "string" && value.trim().length >= (schema.minLength ?? 0) &&
      value.length <= (schema.maxLength ?? Infinity) && (!schema.enum || schema.enum.includes(value)) &&
      (!schema.pattern || new RegExp(schema.pattern, "u").test(value));
  }
  if (schema.type === "array") {
    return Array.isArray(value) && value.length <= schema.maxItems! && value.every(item => matches(schema.items!, item));
  }
  if (!value || typeof value !== "object" || Array.isArray(value)) return false;
  const fields = value as Record<string, unknown>;
  const keys = Object.keys(schema.properties!);
  return Object.keys(fields).length === keys.length &&
    keys.every(key => Object.hasOwn(fields, key) && matches(schema.properties![key], fields[key]));
}
