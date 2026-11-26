import { closeSync, fsyncSync, openSync, readFileSync, writeFileSync } from 'node:fs'

export class Journal {
  constructor(path) {
    this.fd = openSync(path, 'a+', 0o600)
    this.results = new Map()
    this.audits = new Map()
    this.auditIds = new Set()
    this.attempts = []
    this.stopped = false
    try {
      for (const line of readFileSync(this.fd, 'utf8').split('\n').filter(Boolean)) {
        this.apply(JSON.parse(line))
      }
    } catch (error) {
      this.close()
      throw error
    }
  }

  apply(record) {
    if (record.type === 'audit') {
      this.auditIds.add(record.event.id)
      this.audits.set(record.event.id, record.event)
      return
    }
    if (record.type === 'audit_ack') {
      this.audits.delete(record.id)
      return
    }
    if (record.type === 'stop') this.stopped = true
    if (record.type === 'attempt') this.attempts.push(record.at)
    if (record.id) this.results.set(record.id, { result: record.result, ...(record.reason && { reason: record.reason }) })
  }

  append(record) {
    writeFileSync(this.fd, JSON.stringify(record) + '\n')
    fsyncSync(this.fd)
    this.apply(record)
  }

  withinLimits(limits, now = Date.now()) {
    const count = duration => this.attempts.filter(at => at > now - duration).length
    return count(3_600_000) < limits.hour && count(86_400_000) < limits.day
  }

  close() {
    closeSync(this.fd)
  }
}
