'use strict';

// Minimal DOM contract for executing the actual UI event handlers without a browser.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

class Element {
  constructor(tag) {
    this.tagName = tag.toUpperCase();
    this.children = [];
    this.attributes = {};
    this.listeners = {};
    this.textContent = '';
    this.value = '';
  }
  append(node) {
    this.children.push(node);
    if (this.tagName === 'SELECT' && this.children.length === 1) this.value = node.textContent;
  }
  replaceChildren() { this.children = []; }
  setAttribute(name, value) { this.attributes[name] = value; }
  addEventListener(name, handler) { this.listeners[name] = handler; }
  contains(node) { return this === node || this.children.some(child => child.contains(node)); }
  focus() { document.activeElement = this; }
  querySelectorAll(selector) {
    return descendants(this).filter(node => node.tagName === 'BUTTON' &&
      (!selector.includes(':not') || !node.disabled));
  }
}
function descendants(node) {
  return node.children.flatMap(child => [child, ...descendants(child)]);
}
function content(node) {
  return [node.textContent, ...node.children.map(content)].join(' ');
}

const root = new Element('body');
const ids = {};
for (const id of ['role', 'heading', 'view', 'notice', 'nav']) {
  ids[id] = new Element(id === 'role' ? 'select' : 'div');
  root.append(ids[id]);
}
ids.role.value = 'operator';
const document = {
  activeElement: root,
  querySelector: selector => ids[selector.slice(1)],
  querySelectorAll: selector => root.querySelectorAll(selector),
  createElement: tag => new Element(tag),
};
const source = fs.readFileSync(path.join(__dirname, 'app.js'), 'utf8');
const html = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');
vm.runInNewContext(source, { document, structuredClone });
assert.match(html, /connect-src 'none'/);
assert.doesNotMatch(html, /(?:src|href)="https?:/i);
assert.doesNotMatch(source, /\b(?:fetch|XMLHttpRequest|WebSocket|sendBeacon)\b/);

const results = [];
function find(tag, name) {
  return descendants(root).find(node => node.tagName === tag && node.textContent === name);
}
function click(name) {
  const node = find('BUTTON', name);
  assert.ok(node && !node.disabled && node.listeners.click, name);
  node.focus();
  node.listeners.click();
}
function disabled(name) {
  const node = find('BUTTON', name);
  assert.ok(node?.disabled, name);
  assert.ok(descendants(root).some(element => element.id === node.attributes['aria-describedby']));
}
function set(label, value) {
  const node = find('LABEL', label);
  assert.ok(node?.children.length, label);
  node.children[0].value = value;
}
function role(value) {
  ids.role.value = value;
  ids.role.listeners.change();
}
function view(pattern) { assert.match(content(ids.view), pattern); }
function pass(id, observed) {
  results.push({ id, verdict: 'FUNCTIONAL_PASS', scope: 'DOM_CONTRACT_ONLY', observed });
}

click('Agents / Capabilities');
view(/VERIFIED_IN_PROJECT/);
click('Workflows / Builder');
click('Validate');
view(/Đồ thị trống/);
disabled('Simulate');
click('Nạp luồng mẫu');
click('Lưu draft');
click('Validate');
click('Simulate');
const first = ids.notice.textContent;
click('Simulate');
assert.equal(ids.notice.textContent, first);
disabled('Activate');
click('Runs / Evidence');
assert.equal(descendants(ids.view).filter(node => /^pending.*completed · run-mock/.test(node.textContent)).length, 1);
pass('J1', 'Empty graph rejected; fixture produced one repeatable local run and receipt.');

click('Yêu cầu đối soát giả');
view(/Late success: disputed/);
view(/Đối soát: pending/);
pass('J2', 'Reconciliation request recorded without changing unknown.');
click('Kiểm tra binding callback');
view(/409 · binding không khớp/);
view(/receipt-02.*dispatch: 1/);
set('Digest callback giả', 'mock-digest-02');
click('Kiểm tra binding callback');
view(/200 · replay giả, giữ receipt-02/);
pass('N3', 'Wrong digest rejected; identical fixture replay returns the prior receipt.');
disabled('Retry dispatch trả phí');
view(/dispatch: 1/);
pass('N4', 'Paid retry disabled; one dispatch retained.');

click('Content / Channels');
click('Yêu cầu duyệt nội dung');
click('Approvals');
disabled('Duyệt #1');
role('reviewer');
click('Duyệt #1');
click('Content / Channels');
view(/Duyệt nội dung: approved/);
disabled('Publish');
pass('J3', 'Separate reviewer approves a draft and Publish stays disabled.');
role('operator');
click('Tạo phiên bản media mới');
click('Yêu cầu duyệt nội dung');
click('Approvals');
click('Kiểm tra hết hạn #2');
view(/content\.review.*expired/);
assert.equal(find('BUTTON', 'Duyệt #2'), undefined);
click('Workflows / Builder');
set('Ngân sách node #3', 'unapproved');
click('Áp dụng #3');
click('Lưu draft');
click('Validate');
view(/Chi phí chưa biết hoặc chưa duyệt/);
disabled('Simulate');
pass('N2', 'Expired approval and nonzero/unknown budget were blocked.');

role('reviewer');
for (const name of ['Lưu draft', 'Thêm node', 'Simulate']) disabled(name);
role('operator');
set('Quyền node #2', 'missing');
click('Áp dụng #2');
click('Validate');
view(/Thiếu quyền fixture/);
pass('N1', 'Reviewer cannot edit; validator rejects missing fixture permission.');

click('Connections / Permissions');
role('owner');
click('Lưu đề xuất read-only');
view(/Đã lưu đề xuất read-only · mock-property/);
disabled('OAuth live');
pass('J4', 'Saved a synthetic read-only GA4 proposal.');
view(/UNVERIFIED_ACCOUNT_ACCESS/);
pass('N5', 'Unverified account has a readable OAuth block.');

click('Monitoring / Incidents');
click('Chuyển readiness cho Codex');
click('Áp dụng mẫu recovery 200 ×3');
view(/Readiness: closed/);
click('Chuyển backup cho Hostinger và Điều phối');
view(/restore UNKNOWN · escalated/);
pass('J5', 'Readiness escalated and closed; backup escalated with restore UNKNOWN.');

click('Workflows / Builder');
click('Nạp luồng mẫu');
click('Lưu draft');
click('Validate');
click('Simulate');
click('Yêu cầu duyệt workflow');
click('Approvals');
disabled('Duyệt #3');
role('reviewer');
click('Duyệt #3');
role('operator');
click('Workflows / Builder');
click('Fork phiên bản');
view(/Draft v2/);
disabled('Simulate');
click('Approvals');
view(/workflow\.activate.*expired/);
click('Workflows / Builder');
set('Cổng nguồn', '8');
set('Cổng đích', '6');
set('Trường mapping', 'invalid');
click('Nối cổng');
click('Validate');
view(/Có chu trình/);
view(/Mapping không hợp lệ/);
click('Bỏ nối 4');
click('Bỏ nối 1');
click('Validate');
view(/Thiếu cổng bắt buộc/);
set('Loại node', 'Delay/Retry');
click('Thêm node');
view(/#9 · Delay\/Retry/);
click('Lên #9');
click('Xóa #9');
assert.doesNotMatch(content(ids.view), /#9 · Delay\/Retry/);
click('Settings / Audit');
view(/workflow\.activate · approved · reviewer/);
disabled('Kill switch live');

process.stdout.write(JSON.stringify({
  runtime: 'Node ' + process.version, browser: 'BROWSER_NOT_RUN',
  browser_blockers: ['Local Chromium process singleton socket denied (EPERM)', 'Cloud Browser denied file://'],
  results, supplemental: ['cycle', 'invalid mapping', 'missing port', 'fork invalidates mock approval',
    'node add/reorder/remove', 'audit', 'CSP and no external script/style/network API in source'],
  responsive: 'NOT_RUN', keyboard_browser: 'NOT_RUN', screen_reader: 'NOT_RUN',
  external_requests_from_tests: 0, live_backend: 'UNIMPLEMENTED',
}, null, 2) + '\n');
