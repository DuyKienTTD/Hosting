import assert from 'node:assert/strict'
import { createServer } from 'node:http'
import { mkdtempSync, readFileSync, rmSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { after, before, test } from 'node:test'
import { chromium } from 'playwright'
import { Browser } from '../src/browser.js'
import { Journal } from '../src/journal.js'
import { Worker } from '../src/worker.js'

const fixture = readFileSync(new URL('./fixture.html', import.meta.url))
const selectors = JSON.parse(readFileSync(new URL('../selectors/fixture-v2.json', import.meta.url)))
const server = createServer((_, response) => {
  response.setHeader('Content-Type', 'text/html; charset=utf-8')
  response.end(fixture)
})
let chrome, origin
before(async () => {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve))
  origin = `http://127.0.0.1:${server.address().port}`
  chrome = await chromium.launch({ executablePath: process.env.TEST_CHROMIUM_PATH, headless: process.env.TEST_HEADED !== '1' })
})
after(async () => {
  await chrome?.close()
  server.close()
})

async function setup(t) {
  const context = await chrome.newContext()
  const page = await context.newPage()
  const dir = mkdtempSync(join(tmpdir(), 'nick-test-'))
  const path = join(dir, 'delivery.jsonl')
  const journal = new Journal(path)
  t.after(async () => {
    journal.close()
    await context.close()
    rmSync(dir, { recursive: true, force: true })
  })
  await page.goto(origin)
  const messages = []
  const socket = { readyState: 1, send: data => messages.push(JSON.parse(data)) }
  const browser = new Browser(page, { origin, selectors })
  const worker = new Worker(browser, journal)
  await browser.registerTarget(() => worker.targetChanged())
  await worker.attach(socket)
  const receive = msg => worker.receive(socket, msg)
  await receive({ type: 'policy', hour: 1, day: 2, adsEnabled: false, expiresAt: Date.now() + 20_000 })
  const send = { type: 'send', id: 'fixture-job', peer: 'fixture-customer', text: 'Mẫu đồng', expiresAt: Date.now() + 10_000 }
  const permit = async overrides => {
    const request = messages.findLast(message => message.type === 'authorize')
    assert.ok(request)
    await receive({
      ...request, type: 'permit', guard: 'allow', optOut: 'not_opted_out',
      purpose: 'customer_service', adsEnabled: false, expiresAt: Date.now() + 900, ...overrides
    })
  }
  const clicks = () => page.evaluate(() => window.clicks)
  return { page, worker, journal, socket, receive, send, permit, messages, clicks, path }
}

test('reads inbound, waits for authorization, sends once and observes hourly cap', async t => {
  const f = await setup(t)
  await f.worker.tick(f.socket)
  assert.equal(f.messages.find(msg => msg.type === 'inbound')?.id, 'fixture-in')
  await f.receive({ type: 'inbound_ack', peer: f.send.peer, id: 'fixture-in' })
  await f.worker.tick(f.socket)
  assert.equal(f.messages.filter(msg => msg.type === 'inbound' && msg.id === 'fixture-in').length, 1)
  assert.equal(f.messages.find(msg => msg.id === 'fixture-in-other')?.peer, 'fixture-other')
  assert.equal(f.messages.some(msg => msg.peer === 'fixture-group'), false)
  await f.receive(f.send)
  assert.equal(await f.clicks(), 0)
  await f.permit()
  assert.equal(f.messages.at(-1).result, 'sent')
  await f.receive(f.send)
  assert.equal(f.messages.at(-1).result, 'sent')
  await f.receive({ ...f.send, id: 'fixture-new-job' })
  assert.equal(f.messages.at(-1).result, 'rejected')
  assert.equal(await f.clicks(), 1)
})

test('lost echo is terminal across journal reopen', async t => {
  const f = await setup(t)
  await f.page.evaluate(() => { window.hideEcho = true })
  await f.receive(f.send)
  await f.permit()
  assert.equal(f.messages.at(-1).result, 'unknown_delivery')
  const journal = new Journal(f.path)
  try {
    const restarted = new Worker(f.worker.browser, journal)
    restarted.attach(f.socket)
    await restarted.receive(f.socket, f.send)
    assert.equal(f.messages.at(-1).result, 'unknown_delivery')
  } finally {
    journal.close()
  }
  assert.equal(await f.clicks(), 1)
})

for (const optOut of ['unknown', 'opted_out']) {
  test(`blocks ${optOut} at final authorization`, async t => {
    const f = await setup(t)
    await f.receive(f.send)
    await f.permit({ optOut })
    assert.equal(f.messages.at(-1).result, 'rejected')
    assert.equal(await f.clicks(), 0)
  })
}

for (const reason of ['verification', 'warning', 'restricted', 'logged-out', 'server']) {
  test(`stops on ${reason} before click`, async t => {
    const f = await setup(t)
    await f.receive(f.send)
    if (reason === 'server') await f.receive({ type: 'stop' })
    else await f.page.evaluate(reason => {
      const alert = document.createElement('p')
      alert.setAttribute('data-' + reason, '')
      alert.textContent = 'Fixture alert'
      document.body.append(alert)
    }, reason)
    await f.permit()
    assert.ok(f.journal.stopped)
    assert.equal(await f.clicks(), 0)
  })
}

test('blocks a changed recipient at the click boundary', async t => {
  const f = await setup(t)
  await f.receive(f.send)
  await f.page.locator('[data-active-chat]').evaluate(node => { node.dataset.peer = 'fixture-other' })
  await f.permit()
  assert.equal(await f.clicks(), 0)
  assert.equal(f.messages.at(-1).result, 'rejected')
})

test('blocks a stranger with no inbound history', async t => {
  const f = await setup(t)
  await f.page.locator('[data-active-chat] [data-inbound]').evaluate(node => node.remove())
  await f.receive(f.send)
  assert.equal(f.messages.at(-1).result, 'rejected')
  assert.equal(await f.clicks(), 0)
})

test('rejects a permit from a prior socket after reconnect', async t => {
  const f = await setup(t)
  await f.receive(f.send)
  f.socket.readyState = 3
  f.worker.attach({ readyState: 1, send() {} })
  await f.permit()
  assert.equal(await f.clicks(), 0)
  const restarted = new Journal(f.path)
  try {
    assert.equal(restarted.attempts.length, 0)
  } finally {
    restarted.close()
  }
})

test('daily cap survives restart outside hourly window', async t => {
  const f = await setup(t)
  f.journal.append({ type: 'attempt', id: 'fixture-past', result: 'unknown_delivery', at: Date.now() - 7_200_000 })
  const journal = new Journal(f.path)
  try {
    assert.equal(journal.withinLimits({ hour: 1, day: 1 }), false)
    assert.equal(journal.withinLimits({ hour: 1, day: 2 }), true)
  } finally {
    journal.close()
  }
})

test('heartbeat loss terminates the socket', async t => {
  const f = await setup(t)
  let terminated = false
  f.socket.terminate = () => { terminated = true }
  f.worker.lastPong = Date.now() - 15_001
  await f.worker.tick(f.socket)
  assert.equal(terminated, true)
})

for (const variant of [
  { label: 'stranger with inbound', peer: 'fixture-customer', status: 'not_friend', reason: 'not_friend' },
  { label: 'stranger with the same display name as a friend', peer: 'fixture-other', status: 'not_friend', reason: 'not_friend' },
  { label: 'missing friendship selector', peer: 'fixture-customer', status: null, reason: 'friend_status_unknown' }
]) {
  test(`rejects ${variant.label} before typing even if the server sends a permit`, async t => {
    const f = await setup(t)
    const chat = f.page.locator(`main[data-peer="${variant.peer}"]`)
    await chat.locator('[data-friend-status]').evaluate((node, status) => {
      if (status === null) node.remove()
      else node.dataset.friendStatus = status
    }, variant.status)
    const send = { ...f.send, peer: variant.peer }
    await f.receive(send)
    assert.deepEqual(f.messages.at(-1), {
      type: 'result', id: send.id, result: 'rejected', reason: variant.reason
    })
    assert.equal(f.messages.some(message => message.type === 'authorize'), false)
    await f.receive({
      type: 'permit', id: send.id, peer: send.peer, nonce: 'fixture-unsolicited',
      guard: 'allow', optOut: 'not_opted_out', purpose: 'customer_service',
      adsEnabled: false, expiresAt: Date.now() + 900
    })
    assert.equal(await chat.locator('[data-compose]').inputValue(), '')
    assert.equal(await f.clicks(), 0)
    assert.equal(f.journal.attempts.length, 0)
  })
}

for (const [status, reason] of [['not_friend', 'not_friend'], [null, 'friend_status_unknown']]) {
  test(`rejects a valid permit when friendship becomes ${reason} after typing`, async t => {
    const f = await setup(t)
    await f.receive(f.send)
    await f.page.locator('[data-active-chat] [data-friend-status]').evaluate((node, status) => {
      if (status === null) node.remove()
      else node.dataset.friendStatus = status
    }, status)
    await f.permit()
    const rejection = { type: 'result', id: f.send.id, result: 'rejected', reason }
    assert.deepEqual(f.messages.at(-1), rejection)
    await f.receive(f.send)
    assert.deepEqual(f.messages.at(-1), rejection)
    assert.equal(await f.clicks(), 0)
  })
}

for (const cancellation of ['reconnect', 'stop', 'expiration', 'revocation']) {
  test(`cancels a validated permit before Chromium dispatch on ${cancellation}`, async t => {
    const f = await setup(t)
    await f.receive(f.send)
    const browser = f.worker.browser
    const originalSend = browser.send.bind(browser)
    const entered = Promise.withResolvers()
    const release = Promise.withResolvers()
    browser.send = async (...args) => {
      entered.resolve()
      await release.promise
      return originalSend(...args)
    }

    const expiresAt = Date.now() + (cancellation === 'expiration' ? 150 : 950)
    const delivery = f.permit({ expiresAt })
    try {
      await Promise.race([entered.promise, delivery.then(() => assert.fail('permit never reached dispatch'))])
      if (cancellation === 'reconnect') {
        f.socket.readyState = 3
        f.worker.detach(f.socket)
        f.worker.attach({ readyState: 1, send: data => f.messages.push(JSON.parse(data)) })
        await f.worker.receive(f.worker.socket, {
          type: 'policy', hour: 10, day: 10, adsEnabled: false, expiresAt: Date.now() + 20_000
        })
      } else if (cancellation === 'stop') {
        await f.receive({ type: 'stop' })
      } else if (cancellation === 'revocation') {
        const { id, nonce } = f.messages.findLast(message => message.type === 'authorize')
        await f.receive({ type: 'revoke_permit', id, nonce })
      } else {
        await new Promise(resolve => setTimeout(resolve, Math.max(0, expiresAt - Date.now()) + 15))
      }
      if (cancellation !== 'expiration') assert.ok(Date.now() < expiresAt)
    } finally {
      release.resolve()
      await delivery
    }

    await f.worker.receive(f.worker.socket, f.send)
    assert.equal(f.messages.at(-1).result, 'rejected')
    assert.equal(await f.clicks(), 0)
  })
}

for (const [boundary, cancellation] of [
  ['before_evaluate', 'reconnect'],
  ['inside_page', 'reconnect'],
  ['inside_page', 'stop'],
  ['inside_page', 'revocation'],
  ['inside_page', 'kill_switch']
]) {
  test(`page gate blocks ${cancellation} at ${boundary}`, async t => {
    const f = await setup(t)
    await f.receive(f.send)
    const evaluate = f.page.evaluate.bind(f.page)
    const entered = Promise.withResolvers()
    const release = Promise.withResolvers()
    if (boundary === 'inside_page') {
      await f.page.exposeFunction('fixturePauseClick', () => {
        entered.resolve()
        return release.promise
      })
    }
    f.page.evaluate = async (operation, args) => {
      if (!args?.click) return evaluate(operation, args)
      if (boundary === 'inside_page') {
        const source = operation.toString()
        const instrumented = source.replace(
          'if (click) await new Promise(resolve => setTimeout(resolve, 0))',
          'if (click) await globalThis.fixturePauseClick()'
        )
        assert.notEqual(instrumented, source)
        return evaluate(({ source, args }) => (0, eval)(`(${source})`)(args), { source: instrumented, args })
      }
      entered.resolve()
      await release.promise
      return evaluate(operation, args)
    }

    const expiresAt = Date.now() + 990
    const delivery = f.permit({ expiresAt })
    try {
      await Promise.race([entered.promise, delivery.then(() => assert.fail('click never reached its pause'))])
      const { id, nonce } = f.messages.findLast(message => message.type === 'authorize')
      assert.equal(await evaluate(() => globalThis.__ttdNickSendGate?.permit?.id), nonce)
      if (cancellation === 'reconnect') {
        f.socket.readyState = 3
        await f.worker.detach(f.socket)
        await f.worker.attach({ readyState: 1, send: data => f.messages.push(JSON.parse(data)) })
      } else if (cancellation === 'stop') {
        await f.receive({ type: 'stop' })
      } else if (cancellation === 'revocation') {
        await f.receive({ type: 'revoke_permit', id, nonce })
      } else {
        await f.receive({ type: 'policy', hour: 0, day: 2, adsEnabled: false, expiresAt: Date.now() + 20_000 })
      }
      assert.equal(await evaluate(() => globalThis.__ttdNickSendGate?.permit), null)
      assert.ok(Date.now() < expiresAt, 'cancellation must precede expiry')
    } finally {
      release.resolve()
      await delivery
    }
    assert.equal(await f.clicks(), 0)
    assert.ok(Date.now() < expiresAt, 'the click operation must finish before expiry')
    await f.worker.receive(f.worker.socket, f.send)
    assert.equal(f.messages.at(-1).result, 'rejected')
  })
}

for (const change of ['tab', 'new_page', 'popup', 'navigation', 'conversation', 'url']) {
  test(`invalidates the armed permit when changing ${change} before the click`, async t => {
    const f = await setup(t)
    await f.receive(f.send)
    const evaluate = f.page.evaluate.bind(f.page)
    const entered = Promise.withResolvers()
    const release = Promise.withResolvers()
    f.page.evaluate = async (operation, args) => {
      if (args?.click) {
        entered.resolve()
        await release.promise
      }
      return evaluate(operation, args)
    }
    const expiresAt = Date.now() + 990
    const delivery = f.permit({ expiresAt })
    try {
      await Promise.race([entered.promise, delivery.then(() => assert.fail('click never reached its pause'))])
      if (change === 'tab') {
        const other = await f.page.context().newPage()
        await other.bringToFront()
      } else if (change === 'new_page') {
        await f.page.context().newPage()
      } else if (change === 'popup') {
        await Promise.all([f.page.waitForEvent('popup'), evaluate(() => { window.open('/popup') })])
      } else if (change === 'navigation') {
        await f.page.goto(origin + '/next')
      } else if (change === 'conversation') {
        await evaluate(() => {
          document.querySelector('[data-chat-row][data-peer="fixture-other"]').click()
        })
      } else {
        await evaluate(() => history.pushState({}, '', '#other'))
      }
      assert.equal(await evaluate(() => globalThis.__ttdNickSendGate?.permit ?? null), null)
      assert.ok(Date.now() < expiresAt)
    } finally {
      release.resolve()
      await delivery
    }
    assert.equal(f.messages.at(-1).result, 'rejected')
    assert.equal(await f.clicks(), 0)
  })
}

test('revoke after commit emits durable owner audit without another click', async t => {
  const f = await setup(t)
  await f.receive(f.send)
  const evaluate = f.page.evaluate.bind(f.page)
  const committed = Promise.withResolvers()
  const release = Promise.withResolvers()
  f.page.evaluate = async (operation, args) => {
    const result = await evaluate(operation, args)
    if (args?.click) {
      committed.resolve(result)
      await release.promise
    }
    return result
  }
  const delivery = f.permit()
  const { id, nonce } = f.messages.findLast(message => message.type === 'authorize')
  const revoke = { type: 'revoke_permit', id, nonce }
  const event = { type: 'audit_alert', id, code: 'committed_before_revoke', audience: 'owner',
    idempotencyKey: `nick:committed_before_revoke:${id}` }
  try {
    assert.equal((await Promise.race([committed.promise, delivery.then(() => assert.fail('no commit'))])).clicked, true)
    await f.receive(revoke)
    assert.deepEqual(f.messages.at(-1), event)
    const reopened = new Journal(f.path)
    try {
      assert.deepEqual(reopened.audits.get(id), event)
    } finally {
      reopened.close()
    }
  } finally {
    release.resolve()
    await delivery
  }
  await f.receive({ type: 'audit_ack', id, idempotencyKey: event.idempotencyKey })
  await f.receive(revoke)
  await f.receive(f.send)
  assert.equal(f.messages.at(-1).result, 'sent')
  assert.equal(f.messages.filter(message => message.type === 'audit_alert').length, 1)
  assert.equal(await f.clicks(), 1)
})
