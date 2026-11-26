import { readFileSync, mkdirSync } from 'node:fs'
import { join, isAbsolute } from 'node:path'
import { chromium } from 'playwright'
import WebSocket from 'ws'
import { Browser } from './browser.js'
import { Journal } from './journal.js'
import { Worker } from './worker.js'

const { NICK_PROFILE_ROOT, NICK_SERVER_URL, NICK_WORKER_AUTH, NICK_SELECTOR_FILE, NICK_WEB_URL } = process.env
const server = new URL(NICK_SERVER_URL)
const web = new URL(NICK_WEB_URL)
if (server.protocol !== 'wss:' || server.username || server.password || server.search || server.hash ||
  !NICK_WORKER_AUTH || !NICK_PROFILE_ROOT || !isAbsolute(NICK_PROFILE_ROOT)) {
  throw new Error('Invalid worker configuration')
}

const selectors = JSON.parse(readFileSync(NICK_SELECTOR_FILE, 'utf8'))
const fields = ['version', 'ready', 'chatRow', 'active', 'peerAttribute', 'kindAttribute', 'directKind',
  'messageIdAttribute', 'friendStatus', 'friendStatusAttribute', 'inbound', 'outbound', 'body', 'input', 'send']
if (!fields.every(field => typeof selectors[field] === 'string' && selectors[field].length > 0) ||
  !['verification', 'warning', 'restricted', 'logged_out'].every(reason =>
    typeof selectors.stop?.[reason] === 'string' && selectors.stop[reason].length > 0) ||
  ![selectors.peerAttribute, selectors.kindAttribute, selectors.messageIdAttribute, selectors.friendStatusAttribute].every(
    field => /^data-[\w-]+$/.test(field)
  ) || web.username || web.password ||
  (selectors.version.startsWith('fixture-')
    ? !['http://127.0.0.1', 'http://localhost'].includes(web.protocol + '//' + web.hostname)
    : web.origin !== 'https://chat.zalo.me')) throw new Error('Invalid selector configuration')

mkdirSync(NICK_PROFILE_ROOT, { recursive: true })
// Playwright uses a local DevTools pipe. Chrome owns the exclusive profile lock.
const context = await chromium.launchPersistentContext(join(NICK_PROFILE_ROOT, 'chrome'), { channel: 'chrome', headless: false })
try {
  const journal = new Journal(join(NICK_PROFILE_ROOT, 'delivery.jsonl'))
  const restored = context.pages()
  const page = await context.newPage()
  for (const other of restored) await other.close()
  await page.goto(web.href, { waitUntil: 'domcontentloaded' })
  const browser = new Browser(page, { selectors, origin: web.origin })
  const worker = new Worker(browser, journal)
  let socket
  let retry
  let failures = 0
  let exiting = false

  function connect() {
    if (exiting) return
    const connection = new WebSocket(server, {
      headers: { Authorization: `Bearer ${NICK_WORKER_AUTH}` },
      handshakeTimeout: 5_000,
      maxPayload: 64 * 1024,
      rejectUnauthorized: true,
      followRedirects: false
    })
    socket = connection
    let heartbeat
    connection.on('open', () => {
      worker.attach(connection).catch(failClosed)
      heartbeat = setInterval(() => worker.tick(connection).catch(failClosed), 1_000)
    })
    connection.on('message', (data, binary) => {
      if (binary) return connection.terminate()
      let message
      try {
        message = JSON.parse(data.toString())
      } catch {
        return connection.terminate()
      }
      if (message?.type === 'pong') failures = 0
      worker.receive(connection, message).catch(failClosed)
    })
    connection.on('error', () => connection.terminate())
    connection.on('close', () => {
      worker.detach(connection)?.catch(failClosed)
      clearInterval(heartbeat)
      if (!exiting) retry = setTimeout(connect, Math.min(30_000, 1_000 * 2 ** Math.min(failures++, 5)))
    })
  }

  function failClosed() {
    process.exitCode = 1
    return shutdown()
  }

  async function shutdown() {
    if (exiting) return
    exiting = true
    clearTimeout(retry)
    const invalidated = worker.detach(socket)
    socket?.terminate()
    await context.close()
    await invalidated
    // Let any outstanding callbacks settle with the conservative journal entry intact.
  }

  process.once('SIGINT', shutdown)
  process.once('SIGTERM', shutdown)
  context.on('close', shutdown)
  await browser.registerTarget(() => worker.targetChanged().catch(failClosed))
  connect()
} catch {
  await context.close()
  throw new Error('Worker startup failed')
}
