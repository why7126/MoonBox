const { chromium } = require(process.cwd() + '/node_modules/@playwright/test');
const fs = require('node:fs');

const origin = process.argv[2] || 'http://127.0.0.1:18112';
const dir = process.argv[3] || '../../openspec/changes/add-chat-workbench-image-skill-context/evidence/ui';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  const responses = {
    '/api/v1/chat/spaces': { items: [{ id: 'space', name: 'Test Space' }] },
  };
  await page.addInitScript(() => localStorage.setItem('moonbox.session', JSON.stringify({ username: '视觉测试', access_token: 'token' })));
  await page.route('**/api/v1/chat/**', async route => {
    const url = new URL(route.request().url());
    if (url.pathname.endsWith('/spaces')) return route.fulfill({ json: { code: 0, data: [{ id: 'space', name: 'Test Space' }] } });
    if (url.pathname.endsWith('/capabilities')) return route.fulfill({ json: { code: 0, data: { execution_ready: true, reason: 'ready', repositories: [{ id: 'repo', space_id: 'space' }], materials: { max_images: 5, max_image_bytes: 5242880, max_total_image_bytes: 20971520, allowed_image_mime_types: ['image/png', 'image/jpeg', 'image/webp', 'image/gif'], max_files: 8, max_file_bytes: 5242880, max_total_file_bytes: 20971520, allowed_file_mime_types: ['image/png', 'image/jpeg', 'image/webp', 'image/gif', 'application/pdf', 'text/plain'], max_skills: 5, max_skill_summary_chars: 1200, max_prompt_chars: 32000 } } } });
    if (url.pathname.endsWith('/materials')) return route.fulfill({ json: { code: 0, data: { ref_id: 'mat-screen', kind: 'image', name: 'screen.png', mime_type: 'image/png', size_bytes: 5, status: 'ready' } } });
    if (url.pathname.endsWith('/conversations')) return route.fulfill({ json: { code: 0, data: { items: [], total: 0, page: 1, page_size: 20 } } });
    if (url.pathname.endsWith('/skills')) return route.fulfill({ json: { code: 0, data: { items: [{ id: 'req-explore', name: 'req-explore', summary: '需求探索 - 只读分析', source: '.agents/skills/req-explore/SKILL.md', digest: 'abc', injection_scope: 'context_reference_only' }] } } });
    return route.fulfill({ json: { code: 0, data: responses[url.pathname] || {} } });
  });
  fs.mkdirSync(dir, { recursive: true });
  const results = [];
  for (const [theme, width, height] of [['dark', 1440, 900], ['light', 390, 844]]) {
    await page.setViewportSize({ width, height });
    await page.goto(origin + '/chat');
    await page.waitForLoadState('networkidle');
    if (theme === 'light' && await page.getByTestId('chat-shell').getAttribute('data-theme') === 'dark' && await page.getByTestId('chat-theme-toggle').count()) await page.getByTestId('chat-theme-toggle').click();
    await page.getByTestId('chat-prompt').fill('请结合材料分析');
    await page.getByTestId('chat-file-input').setInputFiles({ name: 'screen.png', mimeType: 'image/png', buffer: Buffer.from('image') });
    await page.getByTestId('chat-skill-button').click();
    await page.getByText('Req Explore', { exact: true }).click();
    await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
    await page.screenshot({ path: `${dir}/materials-${theme}-${width}.png`, fullPage: true });
    const styles = await page.evaluate(() => {
      const sample = selector => {
        const element = document.querySelector(selector);
        if (!element) return null;
        const css = getComputedStyle(element);
        return { width: css.width, height: css.height, color: css.color, backgroundColor: css.backgroundColor, borderRadius: css.borderRadius, display: css.display, gap: css.gap, overflow: css.overflow };
      };
      return { composer: sample('.chat-composer'), strip: sample('.chat-material-strip'), inputRow: sample('[data-testid="chat-input-row"]'), richComposer: sample('[data-testid="chat-rich-composer"]'), prompt: sample('[data-testid="chat-prompt"]'), token: sample('[data-testid="chat-image-attachment"]'), skill: sample('[data-testid="chat-skill-token"]'), send: sample('[data-testid="chat-send"]') };
    });
    const skillInsideInput = await page.evaluate(() => !!document.querySelector('[data-testid="chat-input-row"] [data-testid="chat-skill-token"]'));
    const skillInsideRichComposer = await page.evaluate(() => !!document.querySelector('[data-testid="chat-rich-composer"] [data-testid="chat-skill-token"]'));
    const skillInsideAttachmentStrip = await page.evaluate(() => !!document.querySelector('[data-testid="chat-attachment-strip"] [data-testid="chat-skill-token"]'));
    const promptDisplay = await page.evaluate(() => getComputedStyle(document.querySelector('[data-testid="chat-prompt"]')).display);
    const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth);
    if (overflow) throw Error('materials UI overflow at ' + width);
    if (!skillInsideInput || !skillInsideRichComposer || skillInsideAttachmentStrip || promptDisplay !== 'inline') throw Error('skill token inline flow mismatch at ' + width);
    results.push({ theme, width, height, styles, skillInsideInput, skillInsideRichComposer, skillInsideAttachmentStrip, promptDisplay });
  }
  fs.writeFileSync(`${dir}/materials-computed.json`, JSON.stringify({ boundary: 'synthetic API mocks; production Web bundle and real components', screenshots: 2, results }, null, 2));
  await browser.close();
  console.log(JSON.stringify({ screenshots: 2, computed: true, boundary: 'synthetic API mocks' }));
})();
