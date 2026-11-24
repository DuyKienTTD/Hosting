import { type SendBinding, type AdmissionOutcome } from './atomic-send-admission.js';
/** Offline injected authority only. Never constructs consent from botEnabled. */
export interface AtomicAdmissionPort {
  dispatch<T>(binding: SendBinding, transport: () => Promise<T>, nowMs: number): Promise<AdmissionOutcome<T>>;
}
let authority: AtomicAdmissionPort | null = null;
export function setSyntheticAtomicOutboundRuntime(value: AtomicAdmissionPort | null): void { authority=value; }
export class OutboundGuardDenied extends Error {
  readonly reason:string;
  constructor(reason:string){ super('outbound_guard_'+reason);this.reason=reason; }
}
export async function sendWithOutboundGuard(input: {
  threadKey:string;threadId:string;threadType:number;senderId?:string;
  stableKey:string|undefined;send:()=>Promise<unknown>;
}):Promise<unknown>{
  if (!authority) throw new OutboundGuardDenied('missing_atomic_authority');
  const pos=input.threadKey.indexOf(':');
  const accountId=pos>0?input.threadKey.slice(0,pos):'';
  const boundThread=pos>0?input.threadKey.slice(pos+1):'';
  if (!accountId||boundThread!==input.threadId||!input.stableKey) throw new OutboundGuardDenied('invalid_binding');
  const type=input.threadType===0?'dm':input.threadType===1?'group':null;
  if(!type) throw new OutboundGuardDenied('unknown_thread_type');
  // Group sender must be supplied by validated inbound context, never guessed from thread ID.
  const senderId=type==='dm'?input.threadId:input.senderId;
  if(!senderId) throw new OutboundGuardDenied('missing_group_sender_id');
  const binding:SendBinding={accountId,threadId:input.threadId,senderId,
    recipientId:input.threadId,threadType:type,attemptKey:input.stableKey};
  const result=await authority.dispatch(binding,input.send,Date.now());
  if(result.status!=='sent')throw new OutboundGuardDenied(result.reason);
  return result.value;
}
