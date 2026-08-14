import { writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "../../../../src/web/node_modules/@playwright/test/index.mjs";

const outputDir = dirname(fileURLToPath(import.meta.url));
const baseUrl = "http://127.0.0.1:5176/login";

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 960 } });

await page.goto(baseUrl);
await page.waitForLoadState("networkidle");
await page.screenshot({ path: resolve(outputDir, "visual-1440-hidden.png"), fullPage: true });

const password = page.locator('input[name="password"]');
await password.fill("ExamplePass123!");
await page.getByRole("button", { name: "显示密码" }).click();
await page.screenshot({ path: resolve(outputDir, "visual-1440-visible.png"), fullPage: true });

await page.getByRole("button", { name: "隐藏密码" }).click();
const computed = await page.evaluate(() => {
  const container = document.querySelector(".login-password-field");
  const input = document.querySelector('input[name="password"]');
  const button = document.querySelector(".login-password-toggle");
  if (!container || !input || !button) {
    throw new Error("Password visibility elements were not found.");
  }

  const containerStyle = getComputedStyle(container);
  const inputStyle = getComputedStyle(input);
  const buttonStyle = getComputedStyle(button);
  button.focus();
  const focusStyle = getComputedStyle(button);

  return {
    container: { position: containerStyle.position, display: containerStyle.display },
    input: { paddingRight: inputStyle.paddingRight, width: inputStyle.width, height: inputStyle.height },
    button: {
      width: buttonStyle.width,
      height: buttonStyle.height,
      right: buttonStyle.right,
      color: buttonStyle.color,
      borderColor: buttonStyle.borderColor,
    },
    focus: { outlineStyle: focusStyle.outlineStyle, borderColor: focusStyle.borderColor },
  };
});
await writeFile(resolve(outputDir, "computed-style.json"), JSON.stringify(computed, null, 2));

await page.setViewportSize({ width: 390, height: 844 });
await page.reload();
await page.waitForLoadState("networkidle");
await page.screenshot({ path: resolve(outputDir, "visual-mobile-hidden.png"), fullPage: true });

await browser.close();
