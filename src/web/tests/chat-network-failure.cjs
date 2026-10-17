const { chromium, expect } = require('@playwright/test');
const fs = require('node:fs');
const path = require('node:path');

const output = process.env.CHAT_NETWORK_EVIDENCE_DIR || path.resolve('../../logs/chat-network-failure');
const base = process.env.CHAT_BASE_URL || 'http://localhost:39002';
const conversation = { id: 'network', space_id: 'space', repository_id: 'repo', title: '网络异常验收', archived: false, active_turn_id: null };
const scenarios = [
  { name: 'startup', fail: '/spaces', expected: '工作台连接暂时中断' },
  { name: 'binding', fail: '/capabilities', expected: '工作台连接暂时中断' },
  { name: 'messages', fail: '/messages', expected: '消息暂不可读，请稍后重试' },
  { name: 'governance', fail: '/governance-candidates', expected: '已生成' },
  { name: 'turns', fail: '/turns', expected: '已生成' },
  { name: 'events', fail: '/events', expected: '已生成' },
];

(async () => {
  fs.mkdirSync(output, { recursive: true });
  const browser = await chromium.launch();
  const results = [];
  try {
    for (const scenario of scenarios) {
      const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
      const currentConversation = scenario.name === 'events' ? { ...conversation, active_turn_id: 'turn' } : conversation;
      await page.addInitScript(() => localStorage.setItem('moonbox.session', JSON.stringify({ access_token: 'synthetic', username: 'synthetic' })));
      const failedRequests = [];
      await page.route('**/api/**', async route => {
        const url = new URL(route.request().url()), endpoint = url.pathname;
        if (endpoint.endsWith(scenario.fail)) {
          failedRequests.push(endpoint);
          return route.abort('failed');
        }
        let data = {};
        if (endpoint.endsWith('/spaces')) data = [{ id: 'space', name: '验证空间' }];
        else if (endpoint.endsWith('/capabilities')) data = { execution_ready: true, reason: '', repositories: [{ id: 'repo', space_id: 'space' }] };
        else if (endpoint.endsWith('/conversations')) data = { items: [currentConversation], total: 1 };
        else if (endpoint.endsWith('/conversations/network')) data = currentConversation;
        else if (endpoint.endsWith('/messages')) data = { items: [{ id: 'assistant', role: 'assistant', turn_id: 'turn', content: '已生成需求文档。', materials: [], created_at: '2026-09-30T00:01:00Z' }] };
        else if (endpoint.endsWith('/turns')) data = { items: scenario.name === 'events' ? [{ id: 'turn', status: 'running', conversation_id: 'network' }] : [] };
        else if (endpoint.endsWith('/turns/turn')) data = { id: 'turn', status: 'running', conversation_id: 'network' };
        else if (endpoint.endsWith('/objects') || endpoint.endsWith('/governance-candidates')) data = { items: [] };
        else if (endpoint.endsWith('/relations')) data = { primary: null, references: [] };
        else if (endpoint.endsWith('/projects')) data = { current_user: { name: 'synthetic' }, workspaces: [], projects: [{ space_id: 'space', repository_id: 'repo', readonly: false, status: 'connected' }] };
        await route.fulfill({ json: { code: 0, data } });
      });
      await page.goto(`${base}/chat?space_id=space&conversation_id=network`);
      await expect.poll(() => failedRequests.length, { timeout: 15000 }).toBeGreaterThan(0);
      await page.waitForTimeout(250);
      const visible = await page.locator('body').innerText();
      await page.screenshot({ path: path.join(output, `AC-029-${scenario.name}-1440x900.png`) });
      if (/NetworkError when attempting to fetch resource|Failed to fetch/.test(visible)) throw Error(`${scenario.name}: browser-native error leaked`);
      if (!visible.includes(scenario.expected)) throw Error(`${scenario.name}: expected localized/retained text missing: ${scenario.expected}; visible=${visible.slice(0, 700)}`);
      const messageBox = await page.evaluate(expected => {
        const element = [...document.querySelectorAll('p,div,span')].find(node => node.textContent?.trim() === expected);
        if (!element) return null;
        const box = element.getBoundingClientRect(), style = getComputedStyle(element);
        return { tag: element.tagName.toLowerCase(), width: box.width, display: style.display, visibility: style.visibility };
      }, scenario.expected);
      results.push({ scenario: scenario.name, failedRequestCount: failedRequests.length, expectedVisible: scenario.expected, messageBox, nativeErrorVisible: false, savedMessageVisible: visible.includes('已生成需求文档') });
      await page.close();
    }
  } finally { await browser.close(); }
  fs.writeFileSync(path.join(output, 'AC-029-network-failure-matrix.json'), JSON.stringify({ mode: 'served-app-with-synthetic-api-and-browser-network-fault-injection', base, results }, null, 2));
  console.log(`${results.length} network-failure scenarios passed`);
})().catch(error => { console.error(error); process.exitCode = 1; });
