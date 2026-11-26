import { randomUUID } from 'node:crypto'

const id = value => typeof value === 'string' && /^[a-zA-Z0-9_-]{1,100}$/.test(value)
const future = (value, max) => Number.isSafeInteger(value) && value > Date.now() && value <= Date.now() + max
const limit = value => Number.isSafeInteger(value) && value >= 0
const validCommand = msg => id(msg.id) && id(msg.peer) && future(msg.expiresAt, 60_000) &&
  typeof msg.text === 'string' && !!msg.text.trim() && msg.text.length <= 500 && !/[\p{Cc}\p{Zl}\p{Zp}]/u.test(msg.text)

export class Worker {
  constructor(browser, journal) {
    this.browser = browser
    this.journal = journal
    this.acked = new Set()
    this.connectionEpoch = 0
  }

  attach(socket) {
    const invalidated = this.invalidatePermit()
    this.connectionEpoch++
    this.socket = socket
    this.policy = null
    this.lastPong = Date.now()
    this.emit({ type: 'hello', protocol: 1, stopped: this.journal.stopped })
    return invalidated
  }

  detach(socket) {
    if (socket !== this.socket) return
    const invalidated = this.invalidatePermit()
    this.connectionEpoch++
    this.socket = null
    this.policy = null
    return invalidated
  }

  emit(message, socket = this.socket) {
    if (socket?.readyState === 1) socket.send(JSON.stringify(message))
  }

  stop(reason) {
    const invalidated = this.invalidatePermit()
    if (!this.journal.stopped) this.journal.append({ type: 'stop' })
    this.emit({ type: 'stopped', reason })
    return invalidated
  }

  targetChanged() {
    const invalidated = this.invalidatePermit()
    this.connectionEpoch++
    return invalidated
  }

  async invalidatePermit(explicit) {
    const pending = this.pending
    const revoked = explicit ?? (pending && { id: pending.command.id, nonce: pending.nonce })
    const committed = await this.browser.invalidatePermit(revoked)
    if (!committed || this.journal.auditIds.has(committed.id)) return
    const event = {
      type: 'audit_alert', id: committed.id, code: 'committed_before_revoke', audience: 'owner',
      idempotencyKey: `nick:committed_before_revoke:${committed.id}`
    }
    this.journal.append({ type: 'audit', event })
    this.emit(event)
  }

  current(socket = this.socket) {
    return socket?.readyState === 1 && socket === this.socket && !this.journal.stopped &&
      Date.now() - this.lastPong < 15_000 && this.policy?.expiresAt > Date.now()
  }

  async tick(socket) {
    if (Date.now() - this.lastPong >= 15_000) {
      const invalidated = this.detach(socket)
      socket.terminate()
      return invalidated
    }
    this.emit({ type: 'heartbeat', stopped: this.journal.stopped }, socket)
    for (const event of this.journal.audits.values()) this.emit(event, socket)
    if (this.journal.stopped || this.scanning) return
    const scanned = this.pending ? this.browser.snapshot() : this.browser.scan(
      () => !this.pending && !this.journal.stopped && this.socket === socket && socket.readyState === 1
    )
    this.scanning = scanned
    try {
      const state = await scanned
      if (state.stop) return this.stop(state.stop)
      if (!id(state.peer) || this.socket !== socket) return
      for (const message of state.inbound.slice(-50)) {
        if (!id(message.id) || message.text.length > 20_000) continue
        if (!this.acked.has(`${state.peer}:${message.id}`)) {
          this.emit({ type: 'inbound', peer: state.peer, ...message }, socket)
        }
      }
    } catch {
      await this.stop('browser_unavailable')
    } finally {
      this.scanning = null
    }
  }

  async receive(socket, msg) {
    if (socket !== this.socket || !msg || typeof msg !== 'object') return
    if (msg.type === 'revoke_permit') {
      const pending = this.pending
      if (pending?.socket === socket && pending.command.id === msg.id && pending.nonce === msg.nonce) {
        pending.revoked = true
      }
      if (id(msg.id) && id(msg.nonce)) return this.invalidatePermit({ id: msg.id, nonce: msg.nonce })
      return
    }
    if (msg.type === 'audit_ack' && this.journal.audits.get(msg.id)?.idempotencyKey === msg.idempotencyKey && this.journal.audits.has(msg.id)) {
      this.journal.append({ type: 'audit_ack', id: msg.id })
      return
    }
    if (msg.type === 'stop') return this.stop('server_stop')
    if (msg.type === 'pong') {
      this.lastPong = Date.now()
      return
    }
    if (msg.type === 'inbound_ack' && id(msg.peer) && id(msg.id)) {
      if (this.acked.size >= 10_000) this.acked.clear()
      this.acked.add(`${msg.peer}:${msg.id}`)
      return
    }
    if (msg.type === 'policy') {
      this.policy = future(msg.expiresAt, 30_000) && limit(msg.hour) && limit(msg.day) &&
        msg.adsEnabled === false && msg.hour > 0 && msg.day > 0 ? msg : null
      if (!this.policy) {
        if (this.pending) this.pending.revoked = true
        return this.invalidatePermit()
      }
      return
    }
    const result = (value, reason) => this.emit({
      type: 'result', id: msg.id, result: value, ...(reason && { reason })
    }, socket)
    if (!id(msg.id)) return
    if (msg.type === 'send' && this.pending?.command.id === msg.id) return
    const recorded = this.journal.results.get(msg.id)
    if (recorded) return result(recorded.result, recorded.reason)
    if (msg.type === 'send') {
      if (this.pending || !this.current(socket) || !validCommand(msg) || !this.journal.withinLimits(this.policy)) {
        return result('rejected')
      }
      const epoch = this.connectionEpoch
      const pending = { command: msg, socket, epoch, nonce: randomUUID(), phase: 'typing' }
      this.pending = pending
      const current = () => epoch === this.connectionEpoch && this.current(socket) && msg.expiresAt > Date.now()
      let reason
      try {
        await this.scanning
        const prepared = await this.browser.prepare(msg, current)
        reason = prepared.reason
        if (prepared.stop) await this.stop(prepared.stop)
        if (prepared.ready && current()) {
          Object.assign(pending, { phase: 'authorization', before: prepared.before })
          this.emit({ type: 'authorize', id: msg.id, peer: msg.peer, nonce: pending.nonce, text: msg.text }, socket)
          pending.timer = setTimeout(() => {
            this.pending = null
            result('rejected')
          }, Math.min(3_000, msg.expiresAt - Date.now()))
          return
        }
      } catch {
        await this.stop('browser_unavailable')
      }
      this.pending = null
      if (reason) this.journal.append({ type: 'result', id: msg.id, result: 'rejected', reason })
      return result('rejected', reason)
    }

    const pending = this.pending
    if (msg.type !== 'permit' || pending?.phase !== 'authorization' || pending.socket !== socket ||
      msg.id !== pending.command.id || msg.peer !== pending.command.peer || msg.nonce !== pending.nonce) return
    clearTimeout(pending.timer)
    pending.phase = 'sending'
    try {
      if (pending.revoked || pending.epoch !== this.connectionEpoch || !this.current(socket) || !future(msg.expiresAt, 1_000) || pending.command.expiresAt <= Date.now() ||
        msg.guard !== 'allow' || msg.optOut !== 'not_opted_out' || msg.purpose !== 'customer_service' ||
        msg.adsEnabled !== false || !this.journal.withinLimits(this.policy)) return result('rejected')

      // Persist the conservative result before handing control to Chrome.
      this.journal.append({ type: 'attempt', id: msg.id, at: Date.now(), result: 'unknown_delivery' })
      const deadline = Math.min(msg.expiresAt, pending.command.expiresAt, this.policy.expiresAt, this.lastPong + 15_000)
      let outcome = 'unknown_delivery'
      let reason
      try {
        const canClick = () => !pending.revoked && pending.epoch === this.connectionEpoch &&
          this.current(socket) && Date.now() < deadline
        const sent = await this.browser.send(pending.command, deadline, pending.before, canClick, {
          id: pending.nonce, epoch: pending.epoch
        })
        if (sent.stop) await this.stop(sent.stop)
        if (sent.confirmed) outcome = 'sent'
        else if (!sent.clicked) {
          outcome = 'rejected'
          reason = sent.reason
        }
      } catch {
        await this.stop('browser_unavailable')
      }
      if (outcome !== 'unknown_delivery') this.journal.append({ type: 'result', id: msg.id, result: outcome, reason })
      result(outcome, reason)
    } finally {
      this.pending = null
    }
  }
}
