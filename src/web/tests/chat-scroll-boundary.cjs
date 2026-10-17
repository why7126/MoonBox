const { chromium, firefox } = require('@playwright/test');
const fs = require('node:fs');
const path = require('node:path');

const styles = ['globals.css', 'workbench.css', 'chat-workbench.css', 'project-governance.css']
  .map(name => fs.readFileSync(path.resolve(__dirname, '../src/styles', name), 'utf8'))
  .join('\n');
const screenshotDir = path.resolve(__dirname, '../../../logs/bug-0029-scroll-boundary');

const message = (index) => `<div class="chat-message-block turn-assistant"><article class="chat-message">
  <strong>助手</strong><div class="chat-assistant-col"><div class="chat-message-bubble">
  <p>测试消息 ${index}: ${'长对话滚动内容。'.repeat(24)}</p></div></div>
</article></div>`;

function fixture(count) {
  return `<!doctype html><html lang="zh-CN"><meta charset="utf-8"><style>${styles}</style>
    <main class="requirement-center theme-dark chat-shell" data-testid="chat-shell">
      <aside class="rc-sidebar"></aside><section class="chat-main">
        <div class="chat-session-bar">测试会话</div><div class="chat-subbar">对话</div>
        <section class="chat-conversation" data-testid="chat-conversation">
          <div class="chat-message-history">${Array.from({ length: count }, (_, i) => message(i)).join('')}</div>
        </section>
        <form class="chat-composer"><label for="draft">消息</label><textarea id="draft"></textarea>
          <button type="button" id="send">发送</button></form>
      </section>
    </main></html>`;
}

const measure = () => {
  const conversation = document.querySelector('.chat-conversation');
  const composer = document.querySelector('.chat-composer');
  const draft = document.querySelector('#draft');
  const role = document.querySelector('.chat-message > strong');
  const box = composer.getBoundingClientRect();
  return {
    pageOverflow: Math.max(document.documentElement.scrollHeight - document.documentElement.clientHeight,
      document.body.scrollHeight - document.body.clientHeight),
    pageTop: window.scrollY,
    conversationTop: conversation.scrollTop,
    conversationOverflow: conversation.scrollHeight - conversation.clientHeight,
    composerVisible: box.top >= 0 && box.bottom <= innerHeight,
    composerOverflow: getComputedStyle(composer).overflow,
    draftVisible: draft.getBoundingClientRect().bottom <= innerHeight,
    rolePosition: role ? getComputedStyle(role).position : null,
    roleOffsetParent: role ? role.offsetParent?.className : null,
  };
};

(async () => {
  const results = [];
  for (const [engine, browserType] of Object.entries({ firefox, chromium })) {
    const browser = await browserType.launch({ headless: true });
    try {
      for (const viewport of [{ width: 1419, height: 832 }, { width: 1440, height: 900 }]) {
        const page = await browser.newPage({ viewport });
        try {
          for (const count of [0, 1, 28, 0, 28]) {
            await page.setContent(fixture(count));
            const before = await page.evaluate(measure);
            if (before.pageOverflow > 1 || before.pageTop !== 0 || !before.composerVisible || !before.draftVisible) {
              throw new Error(`${engine} ${viewport.width}x${viewport.height} count=${count} initial ${JSON.stringify(before)}`);
            }
            if (count > 0 && (before.rolePosition !== 'absolute' || !before.roleOffsetParent.includes('chat-message'))) {
              throw new Error(`${engine} role positioning: ${JSON.stringify(before)}`);
            }
            if (count === 28) {
              if (before.conversationOverflow <= 0) throw new Error(`${engine} long conversation did not overflow`);
              await page.locator('.chat-conversation').evaluate(el => { el.scrollTop = 0; });
              const top = await page.evaluate(measure);
              fs.mkdirSync(screenshotDir, { recursive: true });
              await page.screenshot({ path: path.join(screenshotDir, `${engine}-${viewport.width}x${viewport.height}-top.png`) });
              await page.locator('.chat-conversation').evaluate(el => { el.scrollTop = el.scrollHeight; });
              const bottom = await page.evaluate(measure);
              await page.screenshot({ path: path.join(screenshotDir, `${engine}-${viewport.width}x${viewport.height}-bottom.png`) });
              if (top.conversationTop !== 0 || Math.abs(bottom.conversationTop - bottom.conversationOverflow) > 1 ||
                bottom.pageOverflow > 1 || bottom.pageTop !== 0 || !bottom.composerVisible) {
                throw new Error(`${engine} scroll boundary: ${JSON.stringify({ top, bottom })}`);
              }
              await page.locator('#draft').fill('synthetic send check');
              await page.locator('#send').click();
              if (await page.locator('#draft').inputValue() !== 'synthetic send check') throw new Error('draft edit lost');
            }
            results.push({ engine, viewport, count, ...before });
          }
        } finally { await page.close(); }
      }
    } finally { await browser.close(); }
  }
  console.log(JSON.stringify({ cases: results.length, screenshotDir,
    maxPageOverflow: Math.max(...results.map(result => result.pageOverflow)),
    longConversationOverflow: results.filter(result => result.count === 28)
      .map(({ engine, viewport, conversationOverflow }) => ({ engine, viewport, conversationOverflow })) }, null, 2));
})().catch(error => { console.error(error); process.exitCode = 1; });
