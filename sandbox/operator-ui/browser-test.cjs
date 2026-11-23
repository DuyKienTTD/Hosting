'use strict';

const assert = require('node:assert/strict');
const { writeFile, mkdir } = require('node:fs/promises');
const { join } = require('node:path');
const { pathToFileURL } = require('node:url');
const { chromium } = require('playwright');

async function main() {
  const output = process.argv[2];
  if (!output) throw new Error('Pass a scratch output directory.');
  await mkdir(output, { recursive: true });
  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_BIN || '/usr/bin/chromium',
    args: ['--no-sandbox', '--disable-background-networking'],
  });
  try {
    const page = await browser.newPage({ viewport: { width: 1280, height: 960 } });
    const errors = [], outbound = [], results = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('request', request => { if (/^https?:/i.test(request.url())) outbound.push(request.url()); });
    await page.route(/^https?:/i, request => request.abort());
    await page.goto(pathToFileURL(join(__dirname, 'index.html')).href);
    const click = name => page.getByRole('button', { name, exact: true }).click();
    const control = name => page.getByRole('button', { name, exact: true });
    const disabled = async name => assert.equal(await control(name).isDisabled(), true, name);
    const visible = async expression => assert.match(await page.locator('main').innerText(), expression);
    const role = name => page.getByLabel('Vai trò mô phỏng').selectOption(name);
    const pass = (id, observed) => results.push({ id, verdict: 'FUNCTIONAL_PASS', observed });

    await click('Agents / Capabilities');
    await page.getByLabel('Nguồn năng lực').selectOption('GA4');
    await visible(/GA4 · DOCUMENTED · UNVERIFIED_ACCOUNT_ACCESS/);
    await click('Workflows / Builder');
    await click('Validate');
    await visible(/Đồ thị trống/);
    await disabled('Simulate');
    await click('Nạp luồng mẫu');
    await click('Lưu draft');
    await click('Validate');
    await click('Simulate');
    const run = (await page.locator('#notice').innerText()).match(/receipt-mock-fnv-[a-f0-9]+/)[0];
    await click('Simulate');
    assert.match(await page.locator('#notice').innerText(), new RegExp(run));
    await disabled('Activate');
    await page.screenshot({ path: join(output, 'builder-1280.png') });
    await click('Runs / Evidence');
    await visible(new RegExp(run));
    assert.equal(await page.getByText(/completed · run-mock/).count(), 1);
    pass('J1', 'Invalid empty graph, then valid fixture, same receipt on repeat, one run, Activate disabled.');

    await click('Yêu cầu đối soát giả');
    await visible(/Đối soát: pending/);
    await visible(/Late success: disputed/);
    await disabled('Retry dispatch trả phí');
    pass('J2', 'Reconciliation recorded locally; immutable unknown and disputed result visible.');
    await click('Kiểm tra binding callback');
    await visible(/409 · binding không khớp/);
    await visible(/receipt-02.*dispatch: 1/);
    await page.getByLabel('Digest callback giả').fill('mock-digest-02');
    await click('Kiểm tra binding callback');
    await visible(/200 · replay giả, giữ receipt-02/);
    pass('N3', 'Wrong digest returns fixture 409; correct replay retains original receipt.');
    await disabled('Retry dispatch trả phí');
    await visible(/outcome_unknown.*khóa retry/);
    await visible(/dispatch: 1/);
    pass('N4', 'Retry control disabled and dispatch remains one after reconciliation and callback checks.');

    await click('Content / Channels');
    await click('Yêu cầu duyệt nội dung');
    await click('Approvals');
    await disabled('Duyệt #1');
    await role('reviewer');
    await click('Duyệt #1');
    await visible(/content\.review.*approved/);
    await click('Content / Channels');
    await visible(/Duyệt nội dung: approved/);
    await disabled('Publish');
    pass('J3', 'Separate requester and reviewer; content.review approves draft, Publish remains disabled.');
    await role('operator');
    await click('Tạo phiên bản media mới');
    await click('Yêu cầu duyệt nội dung');
    await click('Approvals');
    await click('Kiểm tra hết hạn #2');
    await visible(/content\.review.*expired/);
    await role('reviewer');
    assert.equal(await control('Duyệt #2').count(), 0);
    await click('Content / Channels');
    await disabled('Publish');
    await role('operator');
    await click('Workflows / Builder');
    await page.getByLabel('Ngân sách node #3').fill('unapproved');
    await click('Áp dụng #3');
    await click('Lưu draft');
    await click('Validate');
    await visible(/Chi phí chưa biết hoặc chưa duyệt/);
    await disabled('Simulate');
    pass('N2', 'Expired approval cannot be decided; unapproved budget invalidates workflow and blocks simulation.');

    await role('reviewer');
    for (const name of ['Lưu draft', 'Thêm node', 'Simulate']) await disabled(name);
    await role('operator');
    await page.getByLabel('Quyền node #2').selectOption('missing');
    await click('Áp dụng #2');
    await click('Validate');
    await visible(/Thiếu quyền fixture/);
    pass('N1', 'Reviewer controls disabled and a missing fixture scope surfaces a validation issue.');

    await click('Connections / Permissions');
    await role('owner');
    await click('Lưu đề xuất read-only');
    await visible(/Đã lưu đề xuất read-only · mock-property/);
    await disabled('OAuth live');
    pass('J4', 'Local read-only GA4 proposal saved as mock owner; live OAuth unavailable.');
    await visible(/DOCUMENTED · UNVERIFIED_ACCOUNT_ACCESS/);
    await visible(/Tài khoản chưa xác minh/);
    pass('N5', 'Unverified access visibly blocks live OAuth.');

    await click('Monitoring / Incidents');
    await click('Chuyển readiness cho Codex');
    await click('Áp dụng mẫu recovery 200 ×3');
    await visible(/Readiness: closed/);
    await click('Chuyển backup cho Hostinger và Điều phối');
    await visible(/restore UNKNOWN · escalated/);
    pass('J5', 'Readiness escalation/recovery and backup escalation update fake states; restore remains UNKNOWN.');

    await click('Workflows / Builder');
    await click('Nạp luồng mẫu');
    await click('Lưu draft');
    await click('Validate');
    await click('Simulate');
    await click('Yêu cầu duyệt workflow');
    await click('Approvals');
    await role('reviewer');
    await click('Duyệt #3');
    await role('operator');
    await click('Workflows / Builder');
    await click('Fork phiên bản');
    await visible(/Draft v2/);
    await disabled('Simulate');
    await click('Approvals');
    await visible(/workflow\.activate.*expired/);
    await click('Workflows / Builder');
    await page.getByLabel('Cổng nguồn').selectOption('8');
    await page.getByLabel('Cổng đích').selectOption('6');
    await page.getByLabel('Trường mapping').selectOption('invalid');
    await click('Nối cổng');
    await click('Validate');
    await visible(/Có chu trình/);
    await visible(/Mapping không hợp lệ/);
    await click('Bỏ nối 4');
    await click('Bỏ nối 1');
    await click('Validate');
    await visible(/Thiếu cổng bắt buộc/);
    const browserCdp = await page.context().newCDPSession(page);
    const responsive = [];
    for (const width of [360, 768, 1280]) {
      await page.setViewportSize({ width, height: 900 });
      const fits = await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth);
      assert.equal(fits, true, width + 'px overflow');
      responsive.push({ width, horizontal_overflow: false });
    }
    // Render at 2x via Chromium device metrics; CSS viewport halves as in page zoom.
    await browserCdp.send('Emulation.setDeviceMetricsOverride', {
      width: 640, height: 450, deviceScaleFactor: 2, mobile: false,
    });
    assert.equal(await page.evaluate(() => innerWidth === 640 && devicePixelRatio === 2 && document.documentElement.scrollWidth <= innerWidth), true);
    await browserCdp.send('Emulation.clearDeviceMetricsOverride');
    await page.reload();
    await page.keyboard.press('Tab');
    assert.equal(await page.evaluate(() => document.activeElement.textContent), 'Đến nội dung');
    await page.keyboard.press('Enter');
    assert.equal(await page.evaluate(() => document.activeElement.id), 'main');
    await control('Workflows / Builder').focus();
    await page.keyboard.press('Enter');
    assert.equal(await page.evaluate(() => document.activeElement.id), 'heading');
    await click('Nạp luồng mẫu');
    await page.setViewportSize({ width: 360, height: 900 });
    await page.screenshot({ path: join(output, 'builder-360.png') });
    const csp = await page.evaluate(async () => {
      try { await fetch('https://boundary.invalid/'); return false; } catch { return true; }
    });
    assert.equal(csp, true);
    assert.deepEqual(outbound, []);
    assert.deepEqual(errors, []);
    await writeFile(join(output, 'results.json'), JSON.stringify({
      browser: 'Chromium ' + browser.version(), origin: 'file://', results, responsive,
      zoom: '2x Chromium emulation with 640 CSS px; not browser menu zoom',
      keyboard: 'Tab skip link, Enter navigation, focus destination',
      network: { outgoing_http_requests: outbound.length, csp_probe_rejected: csp },
      page_errors: errors, screenshots: ['builder-1280.png', 'builder-360.png'],
      supplemental: ['cycle and invalid mapping', 'missing required port', 'stale workflow approval after fork', 'deterministic repeat simulation'],
      screen_reader: 'NOT_RUN', live_backend: 'UNIMPLEMENTED',
    }, null, 2) + '\n');
  } finally {
    await browser.close();
  }
}
main().catch(error => { console.error(error); process.exitCode = 1; });
