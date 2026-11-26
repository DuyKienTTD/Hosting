import { createCipheriv, createDecipheriv, randomBytes } from "node:crypto";

export class Envelope {
  private readonly key: Buffer;
  constructor(key: Buffer) {
    if (key.length !== 32) throw Error("OA_INVALID_ENCRYPTION_KEY");
    this.key = Buffer.from(key);
  }

  seal(value: string, context: string) {
    const nonce = randomBytes(12);
    const cipher = createCipheriv("aes-256-gcm", this.key, nonce);
    cipher.setAAD(Buffer.from(context));
    return Buffer.concat([nonce, cipher.update(value), cipher.final(), cipher.getAuthTag()]);
  }

  open(value: Buffer, context: string) {
    const decipher = createDecipheriv("aes-256-gcm", this.key, value.subarray(0, 12));
    decipher.setAAD(Buffer.from(context));
    decipher.setAuthTag(value.subarray(-16));
    return Buffer.concat([decipher.update(value.subarray(12, -16)), decipher.final()]).toString("utf8");
  }
}
