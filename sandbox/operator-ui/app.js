'use strict';

const routes = {
  dashboard: 'Dashboard', agents: 'Agents / Capabilities', workflows: 'Workflows / Builder',
  approvals: 'Approvals', runs: 'Runs / Evidence', connections: 'Connections / Permissions',
  monitoring: 'Monitoring / Incidents', content: 'Content / Channels', settings: 'Settings / Audit',
};
const ports = {
  Trigger: [null, 'event'], 'Agent Task': ['event', 'task'], Connector: ['task', 'outcome'],
  'Human Approval': ['outcome', 'outcome'], Condition: ['outcome', 'outcome'],
  'Delay/Retry': ['outcome', 'outcome'], 'Receipt/Evidence': ['outcome', 'receipt'],
  'Stop/Rollback': ['outcome', null],
};
const fixtureTime = '2026-11-23T03:00:00Z';
const unknownRun = Object.freeze({
  state: 'outcome_unknown', digest: 'mock-digest-02', receipt: 'receipt-02', dispatches: 1,
});
const fixtureGraph = ['Trigger', 'Agent Task', 'Connector', 'Receipt/Evidence'];
let nodes = [], edges = [], nextNode = 1, revision = 1, saved, checked, simulated;
let route = 'dashboard', approvalNumber = 0, mediaVersion = 1, proposal = false;
let readiness = 'open', backup = 'open', reconcile = false, callbackError = '';
const approvals = [], archive = [], audit = [], runs = [];
const role = document.querySelector('#role');
const heading = document.querySelector('#heading');
const view = document.querySelector('#view');
const notice = document.querySelector('#notice');
const nav = document.querySelector('#nav');
const canEdit = () => role.value !== 'reviewer';

function element(tag, value, parent = view) {
  const node = document.createElement(tag);
  node.textContent = value;
  parent.append(node);
  return node;
}
function card(title, parent = view) {
  const panel = element('section', '', parent);
  panel.className = 'card';
  element('h2', title, panel);
  return panel;
}
function actions(parent) {
  const row = element('div', '', parent);
  row.className = 'actions';
  return row;
}
function button(label, parent, act, reason) {
  const control = element('button', label, parent);
  if (reason) {
    const note = element('span', reason, parent);
    note.className = 'muted';
    note.id = 'reason-' + document.querySelectorAll('button').length;
    control.disabled = true;
    control.setAttribute('aria-describedby', note.id);
  } else {
    control.addEventListener('click', act);
  }
  return control;
}
function input(label, parent, values, selected) {
  const wrapper = element('label', label, parent);
  if (!values) {
    const field = element('input', '', wrapper);
    field.value = selected || '';
    return field;
  }
  const select = element('select', '', wrapper);
  for (const value of values) element('option', value, select);
  if (selected) select.value = selected;
  return select;
}
function say(message) {
  notice.textContent = message;
}
function go(destination) {
  route = destination;
  say('');
  paint();
  heading.focus();
}
function paint() {
  const focused = document.activeElement;
  const restoreLabel = view.contains(focused) && focused.tagName === 'BUTTON' ? focused.textContent : null;
  nav.replaceChildren();
  for (const [key, label] of Object.entries(routes)) {
    const item = button(label, nav, () => go(key));
    if (key === route) item.setAttribute('aria-current', 'page');
  }
  heading.textContent = routes[route];
  view.replaceChildren();
  screens[route]();
  if (restoreLabel) {
    const next = [...view.querySelectorAll('button:not(:disabled)')].find(item => item.textContent === restoreLabel);
    (next || heading).focus();
  }
}
role.addEventListener('change', () => {
  say('Vai trò giả: ' + role.value);
  paint();
});

// FNV-1a is a stable fixture identifier, not a security digest.
function digest(value) {
  let hash = 2166136261;
  for (const char of JSON.stringify(value)) hash = Math.imul(hash ^ char.charCodeAt(0), 16777619);
  return 'mock-fnv-' + (hash >>> 0).toString(16).padStart(8, '0');
}
function snapshot() {
  return structuredClone({ revision, nodes, edges });
}
function edit(action) {
  if (!canEdit()) return say('403 · thiếu quyền sửa trong demo.');
  action();
  saved = checked = simulated = undefined;
  for (const item of approvals) {
    if (item.operation === 'workflow.activate' && ['pending', 'approved'].includes(item.state)) item.state = 'expired';
  }
  say('Draft đã đổi. Kết quả xác thực, mô phỏng và phê duyệt cũ đã hết hiệu lực.');
  paint();
}
function loadFixture() {
  edit(() => {
    nodes = fixtureGraph.map(type => ({
      id: nextNode++, type, label: type, budget: type === 'Connector' ? '0' : '', access: 'fixture-read',
    }));
    edges = nodes.slice(1).map((node, i) => ({ from: nodes[i].id, to: node.id, field: 'payload' }));
  });
}
function errors() {
  const issues = [];
  if (!nodes.length) issues.push('Đồ thị trống.');
  if (nodes.filter(node => node.type === 'Trigger').length !== 1) issues.push('Cần đúng một Trigger.');
  const byId = new Map(nodes.map(node => [node.id, node]));
  for (const node of nodes) {
    if (ports[node.type][0] && edges.filter(edge => edge.to === node.id).length !== 1) issues.push('Thiếu cổng bắt buộc hoặc nhiều nguồn: #' + node.id);
    if (!node.label.trim()) issues.push('Thiếu tên node: #' + node.id);
    if (node.type === 'Connector' && node.budget !== '0') issues.push('Chi phí chưa biết hoặc chưa duyệt: #' + node.id);
    if (['Agent Task', 'Connector'].includes(node.type) && node.access !== 'fixture-read') issues.push('Thiếu quyền fixture: #' + node.id);
    if (node.type === 'Human Approval') issues.push('Thiếu gate phê duyệt node trong mô phỏng S2: #' + node.id);
  }
  for (const edge of edges) {
    const from = byId.get(edge.from), to = byId.get(edge.to);
    if (!from || !to || !ports[from.type][1] || ports[from.type][1] !== ports[to.type][0] || edge.field !== 'payload') {
      issues.push('Mapping không hợp lệ: #' + edge.from + ' → #' + edge.to);
    }
  }
  const visiting = new Set(), visited = new Set();
  function cyclic(id) {
    if (visiting.has(id)) return true;
    if (visited.has(id)) return false;
    visiting.add(id);
    const loop = edges.filter(edge => edge.from === id).some(edge => cyclic(edge.to));
    visiting.delete(id);
    visited.add(id);
    return loop;
  }
  if (nodes.some(node => cyclic(node.id))) issues.push('Có chu trình trong đồ thị.');
  return issues;
}
function supportedGraph() {
  return nodes.length === fixtureGraph.length && edges.length === fixtureGraph.length - 1
    && nodes.every((node, i) => node.type === fixtureGraph[i])
    && nodes.slice(1).every((node, i) => edges.some(edge => edge.from === nodes[i].id && edge.to === node.id));
}
function makeApproval(operation, version, hash) {
  if (!canEdit()) return say('403 · thiếu quyền tạo yêu cầu.');
  approvals.push({
    id: ++approvalNumber, operation, version, hash, requester: role.value, state: 'pending', budget: 0,
  });
  audit.push('Yêu cầu ' + operation + ' · ' + hash);
  say('Đã gửi yêu cầu giả.');
  paint();
}
function decide(item, state) {
  if (item.state !== 'pending' || role.value === 'operator' || role.value === item.requester) {
    return say('403 · người yêu cầu không được tự quyết định.');
  }
  item.state = state;
  audit.push(item.operation + ' · ' + state + ' · ' + role.value);
  say('Đã ghi quyết định giả: ' + state);
  paint();
}
function workflows() {
  const top = card('Draft v' + revision);
  element('p', saved ? 'Đã lưu trong bộ nhớ · ' + saved.hash : 'Chưa lưu · dữ liệu mất khi tải lại trang.', top);
  const row = actions(top);
  const denied = canEdit() ? '' : 'Reviewer chỉ đọc.';
  button('Nạp luồng mẫu', row, loadFixture, denied);
  button('Lưu draft', row, () => {
    const version = snapshot();
    saved = { version, hash: digest(version) };
    say('Đã lưu ' + saved.hash);
    paint();
  }, denied);
  button('Fork phiên bản', row, () => edit(() => {
    archive.push(saved);
    revision += 1;
  }), denied || (!saved ? 'Lưu draft trước khi fork.' : ''));
  button('Validate', row, () => {
    checked = { hash: digest(snapshot()), issues: errors() };
    say(checked.issues.length ? '422 · đồ thị chưa hợp lệ.' : 'Đồ thị hợp lệ.');
    paint();
  });
  button('Simulate', row, () => {
    const hash = saved.hash;
    simulated = { id: 'run-' + hash, hash, revision, receipt: 'receipt-' + hash };
    if (!runs.some(run => run.id === simulated.id)) runs.push(simulated);
    say('Mô phỏng giả hoàn tất: ' + simulated.receipt);
    paint();
  }, denied || (!saved || checked?.hash !== saved.hash || checked.issues.length ? 'Lưu và Validate thành công trước.' : !supportedGraph() ? 'Chỉ mô phỏng luồng mẫu đã định nghĩa.' : ''));
  button('Yêu cầu duyệt workflow', row, () => makeApproval('workflow.activate', revision, saved.hash),
    denied || (!simulated ? 'Cần kết quả mô phỏng hiện hành.' : ''));
  button('Activate', row, null, 'Cần cổng kiểm tra phía server. S2 chỉ mô phỏng.');
  if (checked?.issues.length) {
    const list = element('ul', '', top);
    for (const issue of checked.issues) element('li', issue, list);
  }
  if (simulated) element('p', simulated.id + ' · ' + simulated.receipt, top);
  if (archive.length) element('p', 'Phiên bản đã fork: ' + archive.map(item => 'v' + item.version.revision + ' · ' + item.hash).join(', '), top);
  const layout = element('div', '');
  layout.className = 'grid';
  const graph = card('Nodes', layout);
  const type = input('Loại node', graph, Object.keys(ports));
  button('Thêm node', graph, () => edit(() => {
    nodes.push({ id: nextNode++, type: type.value, label: type.value, budget: '', access: 'fixture-read' });
  }), denied);
  if (!nodes.length) element('p', 'Chưa có node. Nạp luồng mẫu hoặc thêm node.', graph);
  nodes.forEach((node, index) => {
    const section = card('#' + node.id + ' · ' + node.type, graph);
    const [incoming, outgoing] = ports[node.type];
    element('p', 'Input: ' + (incoming || '—') + ' · Output: ' + (outgoing || '—'), section);
    const label = input('Tên node #' + node.id, section, null, node.label);
    const access = ['Agent Task', 'Connector'].includes(node.type)
      ? input('Quyền node #' + node.id, section, ['fixture-read', 'missing'], node.access) : null;
    const budget = node.type === 'Connector' ? input('Ngân sách node #' + node.id, section, null, node.budget) : null;
    const controls = actions(section);
    button('Áp dụng #' + node.id, controls, () => edit(() => {
      node.label = label.value;
      if (access) node.access = access.value;
      if (budget) node.budget = budget.value;
    }), denied);
    button('Lên #' + node.id, controls, () => edit(() => {
      [nodes[index - 1], nodes[index]] = [nodes[index], nodes[index - 1]];
    }), denied || (index === 0 ? 'Đầu danh sách.' : ''));
    button('Xuống #' + node.id, controls, () => edit(() => {
      [nodes[index + 1], nodes[index]] = [nodes[index], nodes[index + 1]];
    }), denied || (index === nodes.length - 1 ? 'Cuối danh sách.' : ''));
    button('Xóa #' + node.id, controls, () => edit(() => {
      nodes = nodes.filter(item => item !== node);
      edges = edges.filter(edge => edge.from !== node.id && edge.to !== node.id);
    }), denied);
  });
  const mapping = card('Cổng và mapping', layout);
  const from = input('Cổng nguồn', mapping, nodes.filter(node => ports[node.type][1]).map(node => String(node.id)));
  const to = input('Cổng đích', mapping, nodes.filter(node => ports[node.type][0]).map(node => String(node.id)));
  const field = input('Trường mapping', mapping, ['payload', 'invalid']);
  button('Nối cổng', mapping, () => edit(() => {
    edges.push({ from: Number(from.value), to: Number(to.value), field: field.value });
  }), denied || (!from.value || !to.value ? 'Cần cả hai cổng.' : ''));
  for (const [index, edge] of edges.entries()) {
    const line = actions(mapping);
    element('span', '#' + edge.from + ' → #' + edge.to + ' · ' + edge.field, line);
    button('Bỏ nối ' + (index + 1), line, () => edit(() => edges.splice(index, 1)), denied);
  }
}

const screens = {
  dashboard() {
    const panel = card('Tổng quan Sandbox');
    element('p', runs.length + ' lượt giả · ' + approvals.filter(item => item.state === 'pending').length + ' yêu cầu chờ duyệt', panel);
    element('p', 'KPI kinh doanh: PROVISIONAL_BIZ02. Nguồn: fixture S2.', panel);
    button('Mở Builder', panel, () => go('workflows'));
  },
  agents() {
    const panel = card('Năng lực giả và bằng chứng');
    const filter = input('Nguồn năng lực', panel, ['Tất cả', 'Hermes', 'GA4', 'Connector fixture']);
    const results = element('ul', '', panel);
    const capabilities = {
      Hermes: 'DOCUMENTED · quyền tài khoản đích chưa xác minh',
      GA4: 'DOCUMENTED · UNVERIFIED_ACCOUNT_ACCESS',
      'Connector fixture': 'VERIFIED_IN_PROJECT · fake offline PR #10/#13',
    };
    function show() {
      results.replaceChildren();
      for (const [name, value] of Object.entries(capabilities)) {
        if (filter.value === 'Tất cả' || filter.value === name) element('li', name + ' · ' + value, results);
      }
    }
    filter.addEventListener('change', show);
    show();
    element('p', 'VERIFIED_IN_SESSION: chưa có tài khoản live được xác minh trong phiên demo.', panel);
  },
  workflows,
  approvals() {
    const panel = card('Hàng chờ duyệt');
    if (!approvals.length) element('p', 'Chưa có yêu cầu.', panel);
    for (const item of approvals) {
      const detail = card('Yêu cầu #' + item.id, panel);
      element('p', item.operation + ' · v' + item.version + ' · ' + item.hash + ' · ' + item.state, detail);
      element('p', 'Requester: ' + item.requester + ' · ngân sách giả: 0', detail);
      if (item.state !== 'pending') continue;
      const reason = role.value === item.requester ? 'Không tự duyệt yêu cầu.' : role.value === 'operator' ? 'Thiếu quyền reviewer.' : '';
      button('Duyệt #' + item.id, detail, () => decide(item, 'approved'), reason);
      button('Từ chối #' + item.id, detail, () => decide(item, 'rejected'), reason);
      button('Kiểm tra hết hạn #' + item.id, detail, () => {
        item.state = 'expired';
        say('Đồng hồ fixture đã vượt cửa sổ duyệt.');
        paint();
      });
    }
  },
  runs() {
    const list = card('Run mô phỏng');
    if (!runs.length) element('p', 'Chưa có lượt mô phỏng từ Builder.', list);
    for (const run of runs) {
      element('p', 'pending → working → sending → completed · ' + run.id + ' · v' + run.revision + ' · ' + run.hash + ' · ' + run.receipt + ' · ' + fixtureTime, list);
    }
    const fixture = card('run-unknown-02 · outcome_unknown');
    element('p', 'pending → working → sending → outcome_unknown · fixture ' + fixtureTime, fixture);
    element('p', 'job-02 · task-02 · correlation-02 · ' + unknownRun.digest + ' · ' + unknownRun.receipt + ' (chỉ đọc) · dispatch: ' + unknownRun.dispatches, fixture);
    element('p', 'Late success: disputed · outcome gốc được giữ.', fixture);
    button('Yêu cầu đối soát giả', fixture, () => {
      reconcile = true;
      say('Đã ghi yêu cầu đối soát · không dispatch lại.');
      paint();
    }, canEdit() ? (reconcile ? 'Đã gửi yêu cầu.' : '') : 'Reviewer chỉ đọc.');
    if (reconcile) element('p', 'Đối soát: pending', fixture);
    const callbackDigest = input('Digest callback giả', fixture, null, 'mock-wrong-digest');
    button('Kiểm tra binding callback', fixture, () => {
      callbackError = callbackDigest.value === unknownRun.digest
        ? '200 · replay giả, giữ ' + unknownRun.receipt + '.'
        : '409 · binding không khớp. Receipt và dispatch giữ nguyên.';
      say(callbackError);
      paint();
    });
    if (callbackError) element('p', callbackError, fixture);
    button('Retry dispatch trả phí', fixture, null, 'outcome_unknown: khóa retry và mọi side effect.');
  },
  connections() {
    const panel = card('GA4 · fixture chỉ đọc');
    element('p', 'DOCUMENTED · UNVERIFIED_ACCOUNT_ACCESS · BIZ-01 PR #12', panel);
    element('p', proposal ? 'Đã lưu đề xuất read-only · mock-property' : 'Chưa lưu đề xuất kết nối.', panel);
    button('Lưu đề xuất read-only', panel, () => {
      proposal = true;
      say('Đã lưu đề xuất sandbox.');
      paint();
    }, role.value === 'owner' ? '' : 'Chọn owner giả để ghi đề xuất.');
    button('OAuth live', panel, null, 'Tài khoản chưa xác minh. Không có kết nối OAuth.');
  },
  monitoring() {
    const panel = card('Tín hiệu giả · WS-02 PR #8');
    element('p', 'n8n readiness 503 ×3 · health 200 · Hermes dashboard 200 · inference chưa đo.', panel);
    element('p', 'Readiness: ' + readiness, panel);
    button('Chuyển readiness cho Codex', panel, () => {
      readiness = 'escalated · Codex';
      paint();
    }, !canEdit() ? 'Reviewer chỉ đọc.' : readiness !== 'open' ? 'Đã chuyển.' : '');
    button('Áp dụng mẫu recovery 200 ×3', panel, () => {
      readiness = 'closed · 200 ×3, không restart/OOM mới';
      paint();
    }, canEdit() && readiness.startsWith('escalated') ? '' : 'Cần chuyển incident trước.');
    element('p', 'Backup 216 h > 192 h · restore UNKNOWN · ' + backup, panel);
    button('Chuyển backup cho Hostinger và Điều phối', panel, () => {
      backup = 'escalated · Hostinger + Điều phối';
      paint();
    }, !canEdit() ? 'Reviewer chỉ đọc.' : backup !== 'open' ? 'Đã chuyển.' : '');
    element('p', 'Thao tác hệ thống, restore và cảnh báo thật không khả dụng.', panel);
  },
  content() {
    const panel = card('Draft media giả · v' + mediaVersion);
    element('p', 'Kênh mẫu: video ngắn · nội dung synthetic · không render hoặc publish.', panel);
    const hash = digest({ mediaVersion, fixture: 'media' });
    const item = approvals.findLast(row => row.operation === 'content.review' && row.hash === hash);
    element('p', 'Duyệt nội dung: ' + (item?.state || 'chưa yêu cầu'), panel);
    button('Tạo phiên bản media mới', panel, () => {
      if (item && ['approved', 'pending'].includes(item.state)) item.state = 'expired';
      mediaVersion += 1;
      paint();
    }, canEdit() ? '' : 'Reviewer chỉ đọc.');
    button('Yêu cầu duyệt nội dung', panel, () => makeApproval('content.review', mediaVersion, hash),
      canEdit() ? (['pending', 'approved'].includes(item?.state) ? 'Phiên bản đã có yêu cầu hoặc quyết định.' : '') : 'Reviewer chỉ đọc.');
    button('Publish', panel, null, 'Phê duyệt nội dung không cấp quyền xuất bản. Cần consent và gate riêng.');
  },
  settings() {
    const panel = card('Audit phiên mô phỏng');
    element('p', 'Nguồn: bộ nhớ trình duyệt; dữ liệu mất khi tải lại.', panel);
    if (!audit.length) element('p', 'Chưa có sự kiện audit.', panel);
    const list = element('ul', '', panel);
    for (const event of audit) element('li', fixtureTime + ' · ' + event, list);
    button('Kill switch live', panel, null, 'Cần policy và quyền phía server. Điều khiển live bị khóa.');
  },
};
paint();
