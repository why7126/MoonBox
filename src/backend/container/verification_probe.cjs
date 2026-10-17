'use strict';
const { chromium, firefox } = require('/opt/moonbox-verification/node_modules/playwright');
const { execFileSync } = require('node:child_process');

async function main() {
  const versions = {};
  for (const [name, type] of Object.entries({ chromium, firefox })) {
    process.stderr.write(`probe_${name}_starting\n`);
    const browser = await type.launch({ headless: true, timeout: 20000 });
    try {
      versions[name] = browser.version();
    } finally {
      await browser.close();
    }
    process.stderr.write(`probe_${name}_ready\n`);
  }
  const pnpmVersion = execFileSync('pnpm', ['--version'], { encoding: 'utf8', timeout: 5000 }).trim();
  process.stdout.write(JSON.stringify({ status: 'ready', browsers: versions,
    node_version: process.version.replace(/^v/, ''), pnpm_version: pnpmVersion }) + '\n');
}

main().catch(() => {
  process.stderr.write('browser_start_failed\n');
  process.exitCode = 1;
});
