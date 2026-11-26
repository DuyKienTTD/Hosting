import { randomInt, randomUUID } from 'node:crypto'
import { setTimeout as delay } from 'node:timers/promises'

// This function also runs in Chrome. Keep every dependency inside it.
export async function inspect({ selectors: s, origin, peer, text, deadline, click, chatAction, permit }) {
  // Yield once so control updates can run before entering the synchronous click task.
  if (click) await new Promise(resolve => setTimeout(resolve, 0))
  if (location.origin !== origin) return { stop: 'unexpected_origin' }
  for (const [reason, selector] of Object.entries(s.stop)) {
    if ([...document.querySelectorAll(selector)].some(node => node.getClientRects().length)) {
      return { stop: reason }
    }
  }
  if (!document.querySelector(s.ready)?.getClientRects().length) return { stop: 'ui_unrecognized' }
  const rows = () => [...document.querySelectorAll(s.chatRow)].filter(node =>
    node.getClientRects().length > 0 && node.getAttribute(s.kindAttribute) === s.directKind)
  if (chatAction === 'list') return { peers: rows().map(node => node.getAttribute(s.peerAttribute)) }
  if (chatAction === 'open') {
    const matches = rows().filter(node => node.getAttribute(s.peerAttribute) === peer)
    if (matches.length !== 1) return { opened: false }
    matches[0].click()
    return { opened: true }
  }
  const active = document.querySelectorAll(s.active)
  const target = active.length === 1 ? active[0] : null
  const matches = !!target && target.getClientRects().length > 0 &&
    target.getAttribute(s.peerAttribute) === peer && target.getAttribute(s.kindAttribute) === s.directKind
  // Read relationship evidence only from the active chat for the requested peer.
  const markers = matches ? target.querySelectorAll(s.friendStatus) : []
  const marker = markers.length === 1 ? markers[0] : null
  const status = marker?.checkVisibility({ visibilityProperty: true })
    ? marker.getAttribute(s.friendStatusAttribute) : null
  const friendRejection = status === 'friend' ? undefined
    : status === 'not_friend' ? 'not_friend' : 'friend_status_unknown'

  const messages = selector => target?.getClientRects().length ? [...target.querySelectorAll(selector)].flatMap(node => {
    const id = node.getAttribute(s.messageIdAttribute)
    const body = node.querySelector(s.body)
    return id && body ? [{ id, text: body.textContent }] : []
  }) : []
  if (!click) return {
    matches,
    friendRejection,
    peer: target?.getAttribute(s.kindAttribute) === s.directKind ? target.getAttribute(s.peerAttribute) : null,
    inbound: messages(s.inbound),
    outbound: messages(s.outbound)
  }

  if (matches && friendRejection) return { clicked: false, reason: friendRejection }

  const input = target?.querySelector(s.input)
  const button = target?.querySelector(s.send)
  if (!matches || !target.querySelector(s.inbound) || !button?.getClientRects().length ||
    button.matches(':disabled,[aria-disabled="true"]') || (input?.value ?? input?.textContent) !== text ||
    Date.now() >= deadline) return { clicked: false }
  const gate = globalThis.__ttdNickSendGate
  if (document.visibilityState !== 'visible' || !document.hasFocus() ||
    !gate || gate.permit?.id !== permit.id || gate.permit.epoch !== permit.epoch ||
    gate.permit.pageId !== permit.pageId || gate.permit.peer !== peer ||
    gate.permit.url !== location.href || gate.target !== target ||
    Date.now() >= Math.min(deadline, gate.permit.deadline)) return { clicked: false }
  gate.committed = { id: permit.jobId, nonce: permit.id }
  gate.permit = null
  button.click()
  return { clicked: true }
}

export class Browser {
  constructor(page, config) {
    this.page = page
    this.config = config
    this.lastScanned = null
    this.gateRevision = 0
    this.pageId = randomUUID()
  }

  async registerTarget(onChange) {
    const context = this.page.context()
    const session = await context.newCDPSession(this.page)
    this.targetSession = session
    const { targetInfo } = await session.send('Target.getTargetInfo')
    this.targetId = targetInfo.targetId
    await session.send('Emulation.setFocusEmulationEnabled', { enabled: false })
    context.on('page', onChange)
    this.page.on('popup', onChange)
    this.page.on('close', onChange)
    this.page.on('framenavigated', frame => {
      if (frame === this.page.mainFrame()) onChange()
    })
    session.on('disconnected', onChange)
    await session.send('Target.setDiscoverTargets', { discover: true })
    for (const event of ['Target.targetCreated', 'Target.targetInfoChanged']) {
      session.on(event, ({ targetInfo: changed }) => {
        if (changed.type === 'page' && changed.browserContextId === targetInfo.browserContextId) onChange()
      })
    }
    session.on('Target.targetDestroyed', ({ targetId }) => {
      if (targetId === this.targetId) onChange()
    })
  }

  async isSoleTarget() {
    const pages = this.page.context().pages()
    if (pages.length !== 1 || pages[0] !== this.page || !this.targetSession) return false
    const { targetInfo } = await this.targetSession.send('Target.getTargetInfo')
    const remaining = this.page.context().pages()
    return targetInfo.targetId === this.targetId && remaining.length === 1 && remaining[0] === this.page
  }

  snapshot(peer) {
    return this.page.evaluate(inspect, { ...this.config, peer })
  }

  async scan(current) {
    const list = await this.page.evaluate(inspect, { ...this.config, chatAction: 'list' })
    if (list.stop) return list
    const peers = [...new Set(list.peers.filter(peer => typeof peer === 'string' && /^[a-zA-Z0-9_-]{1,100}$/.test(peer)))].sort()
    const peer = peers.find(peer => this.lastScanned === null || peer > this.lastScanned) ?? peers[0]
    if (peer && current()) {
      const state = await this.open(peer)
      this.lastScanned = peer
      if (state.stop) return state
      if (state.matches) return state
    }
    return this.snapshot()
  }

  async open(peer) {
    const state = await this.snapshot(peer)
    if (state.stop || state.matches) return state
    const opened = await this.page.evaluate(inspect, { ...this.config, peer, chatAction: 'open' })
    if (opened.stop) return opened
    if (!opened.opened) return { matches: false }
    const until = Date.now() + 750
    do {
      const state = await this.snapshot(peer)
      if (state.stop || state.matches) return state
      await delay(50)
    } while (Date.now() < until)
    return { matches: false }
  }

  async prepare(command, current) {
    const { page, config: { selectors: s } } = this
    if (!current()) return { ready: false }
    const state = await this.open(command.peer)
    if (state.stop) return state
    if (!state.matches || !current()) return { ready: false }
    if (state.friendRejection) return { ready: false, reason: state.friendRejection }
    if (!state.inbound.length) return { ready: false }

    // Resolve each keystroke against the same immutable recipient ID.
    const target = page.locator(`${s.active}[${s.peerAttribute}="${command.peer}"]`)
    const input = target.locator(s.input)
    if (await input.evaluate(node => node.value ?? node.textContent)) return { ready: false }
    const before = new Set(state.outbound.map(message => message.id))
    for (const character of command.text) {
      if (!current()) return { ready: false }
      const state = await this.snapshot(command.peer)
      if (state.stop) return state
      if (!state.matches || !current()) return { ready: false }
      if (state.friendRejection) return { ready: false, reason: state.friendRejection }
      await input.pressSequentially(character, { timeout: 500 })
      await delay(randomInt(35, 81))
    }
    return { ready: true, before }
  }

  updateGate(permit = null, revoked = null) {
    const revision = ++this.gateRevision
    const { origin, selectors } = this.config
    return this.page.evaluate(({ revision, permit, revoked, origin, selectors: s }) => {
      if (location.origin !== origin) return { armed: false }
      const gate = globalThis.__ttdNickSendGate ??= { revision: 0, permit: null }
      const committed = revoked?.nonce === gate.committed?.nonce && revoked?.id === gate.committed?.id
        ? gate.committed : undefined
      // Read commit evidence even if this clear was overtaken by another update.
      if (revision <= gate.revision) return { armed: false, committed }
      gate.revision = revision
      if (!permit) {
        if (!revoked || !gate.permit || gate.permit.id === revoked.nonce) gate.permit = null
        return { armed: false, committed }
      }

      const active = document.querySelectorAll(s.active)
      const target = active.length === 1 ? active[0] : null
      if (!target || target.getAttribute(s.peerAttribute) !== permit.peer ||
        document.visibilityState !== 'visible' || !document.hasFocus()) return { armed: false }
      if (!gate.observer) {
        const clear = () => { gate.permit = null }
        window.addEventListener('blur', clear)
        window.addEventListener('focus', clear)
        window.addEventListener('pagehide', clear)
        document.addEventListener('visibilitychange', clear)
        window.navigation?.addEventListener('currententrychange', clear)
        gate.observer = new MutationObserver(() => {
          if (!gate.permit) return
          const active = document.querySelectorAll(s.active)
          if (active.length !== 1 || active[0] !== gate.target ||
            gate.target.getAttribute(s.peerAttribute) !== gate.permit.peer ||
            gate.target.getAttribute(s.kindAttribute) !== s.directKind) clear()
        })
        gate.observer.observe(document, { subtree: true, childList: true, attributes: true })
      }
      gate.target = target
      gate.permit = { ...permit, url: location.href }
      return { armed: true }
    }, { revision, permit, revoked, origin, selectors })
  }

  async invalidatePermit(revoked) {
    try {
      return (await this.updateGate(null, revoked)).committed
    } catch {
      await this.page.close()
    }
  }

  async send(command, deadline, before, canClick, identity) {
    if (!canClick()) return { clicked: false }
    const permit = { ...identity, deadline, pageId: this.targetId ?? this.pageId, peer: command.peer, jobId: command.id }
    if (!await this.isSoleTarget() || !canClick() || !(await this.updateGate(permit)).armed ||
      !await this.isSoleTarget() || !canClick()) return { clicked: false }
    const state = await this.page.evaluate(inspect, {
      ...this.config, peer: command.peer, text: command.text, deadline, click: true, permit
    })
    if (!state.clicked) return state
    const expires = Date.now() + 2_000
    while (Date.now() < expires) {
      const state = await this.snapshot(command.peer)
      if (state.stop) return { ...state, clicked: true }
      if (state.matches && state.outbound.some(message =>
        !before.has(message.id) && message.text === command.text)) return { clicked: true, confirmed: true }
      await delay(100)
    }
    return { clicked: true }
  }
}
