'use strict';
const fs = require('node:fs');
const path = require('node:path');
const playwright = process.env.MOONBOX_VERIFICATION_PROJECT_ARTIFACT
  ? require('/dependencies/node_modules/@playwright/test')
  : require('/opt/moonbox-verification/node_modules/playwright');

async function readPlan() {
  let input = '';
  for await (const chunk of process.stdin) {
    input += chunk;
    if (input.length > 16384) throw new Error('plan_too_large');
  }
  return JSON.parse(input);
}

function validate(plan) {
  if (!plan || !['chromium', 'firefox'].includes(plan.browser)) throw new Error('browser_invalid');
  if (!Array.isArray(plan.viewports) || plan.viewports.length < 1 || plan.viewports.length > 4) throw new Error('viewports_invalid');
  if (typeof plan.url !== 'string' || !/^https?:\/\/[A-Za-z0-9._:-]+(?:\/[A-Za-z0-9._~/?=&%-]*)?$/.test(plan.url)) throw new Error('target_invalid');
  if (!Array.isArray(plan.selectors) || plan.selectors.length > 20 || plan.selectors.some(s => typeof s !== 'string' || s.length > 160)) throw new Error('selectors_invalid');
  if (!Array.isArray(plan.steps) || plan.steps.length > 20) throw new Error('steps_invalid');
  for (const step of plan.steps) {
    if (!step || !['click', 'fill', 'reload', 'expect_visible', 'expect_text'].includes(step.action)) throw new Error('steps_invalid');
    const keys = Object.keys(step).sort().join(',');
    const expected = step.action === 'reload' ? 'action' :
      ['fill', 'expect_text'].includes(step.action) ? 'action,selector,value' : 'action,selector';
    if (keys !== expected) throw new Error('steps_invalid');
    if (step.action !== 'reload' && (typeof step.selector !== 'string' || !step.selector.length || step.selector.length > 160)) throw new Error('steps_invalid');
    if ('value' in step && (typeof step.value !== 'string' || !step.value.length || step.value.length > 500)) throw new Error('steps_invalid');
  }
  for (const viewport of plan.viewports) {
    if (!Number.isInteger(viewport.width) || viewport.width < 320 || viewport.width > 3840 ||
        !Number.isInteger(viewport.height) || viewport.height < 320 || viewport.height > 2160) throw new Error('viewport_invalid');
  }
}

async function main() {
  const plan = await readPlan();
  validate(plan);
  const type = playwright[plan.browser];
  const browser = await type.launch({ headless: true, timeout: 20000 });
  const result = { category: 'real_browser', browser: plan.browser, browser_version: browser.version(), viewports: [] };
  try {
    for (const viewport of plan.viewports) {
      const page = await browser.newPage({ viewport });
      try {
        const response = await page.goto(plan.url, { waitUntil: 'domcontentloaded', timeout: 20000 });
        if (!response || response.status() >= 400) throw new Error('target_response_failed');
        for (const step of plan.steps) {
          try {
            if (step.action === 'reload') {
              await page.reload({ waitUntil: 'domcontentloaded', timeout: 20000 });
              continue;
            }
            const locator = page.locator(step.selector).first();
            if (step.action === 'click') await locator.click({ timeout: 10000 });
            if (step.action === 'fill') await locator.fill(step.value, { timeout: 10000 });
            if (step.action === 'expect_visible') await locator.waitFor({ state: 'visible', timeout: 10000 });
            if (step.action === 'expect_text' && !(await locator.innerText({ timeout: 10000 })).includes(step.value)) throw new Error('expect_text');
          } catch (_) {
            throw new Error('step_failed');
          }
        }
        const styles = {};
        for (const selector of plan.selectors) {
          const locator = page.locator(selector).first();
          if (await locator.count() === 0) throw new Error('selector_missing');
          styles[selector] = await locator.evaluate(element => {
            const css = getComputedStyle(element);
            return { display: css.display, visibility: css.visibility, color: css.color,
                     backgroundColor: css.backgroundColor, fontSize: css.fontSize };
          });
        }
        const filename = `${plan.browser}-${viewport.width}x${viewport.height}.png`;
        await page.screenshot({ path: path.join('/evidence', filename), fullPage: true });
        result.viewports.push({ ...viewport, screenshot: filename, styles, assertion_count: plan.selectors.length + plan.steps.length + 1 });
      } finally {
        await page.close();
      }
    }
  } finally {
    await browser.close();
  }
  process.stdout.write(JSON.stringify(result) + '\n');
}

main().catch(error => {
  if (process.env.MOONBOX_VERIFICATION_DEBUG === '1') process.stderr.write(String(error && error.stack || error) + '\n');
  const code = ['plan_too_large', 'browser_invalid', 'viewports_invalid', 'target_invalid', 'selectors_invalid',
                'steps_invalid', 'viewport_invalid', 'target_response_failed', 'selector_missing', 'step_failed'].includes(error.message)
    ? error.message : 'browser_acceptance_failed';
  process.stderr.write(code + '\n');
  process.exitCode = 1;
});
