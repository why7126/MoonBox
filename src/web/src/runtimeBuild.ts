declare const __MOONBOX_BUILD_ID__: string;

const BUILD_ID = typeof __MOONBOX_BUILD_ID__ === "string" && __MOONBOX_BUILD_ID__ ? __MOONBOX_BUILD_ID__ : "dev";
const BUILD_STORAGE_KEY = "moonbox.web.build-id";
const RELOAD_STORAGE_KEY = "moonbox.web.reload-target";
const LEGACY_GOVERNANCE_PANEL_PATTERNS = [
  /待\s*应用\s*成果/,
  /查\s*看\s*成果/,
  /审\s*阅\s*治理\s*成果/,
  /确认\s*应用/,
  /执行\s*成果\s*保存在\s*独立\s*副本中/,
];

function scriptAssetPaths(doc: Document) {
  return Array.from(doc.scripts)
    .map(script => script.getAttribute("src") || "")
    .filter(src => src.endsWith(".js"))
    .map(src => new URL(src, doc.baseURI).pathname)
    .filter(Boolean);
}

function latestHtmlAssetPaths(html: string, baseUrl: string) {
  const matches = Array.from(html.matchAll(/<script\b[^>]*\bsrc=["']([^"']+\.js)["'][^>]*>/g));
  return matches.map(match => new URL(match[1], baseUrl).pathname).filter(Boolean);
}

export function removeLegacyGovernancePanels(doc: Document = document) {
  let removed = 0;
  const candidates = Array.from(doc.querySelectorAll<HTMLElement>(
    ".chat-main > .pg-result, [data-testid='governance-result-preview'], [aria-label], dialog",
  ));
  for (const node of candidates) {
    const text = `${node.getAttribute("aria-label") || ""} ${node.textContent || ""}`;
    if (!LEGACY_GOVERNANCE_PANEL_PATTERNS.some(pattern => pattern.test(text))) continue;
    node.remove();
    removed += 1;
  }
  return removed;
}

export async function ensureCurrentRuntimeBundle(options: {
  doc?: Document;
  location?: Pick<Location, "href" | "reload">;
  storage?: Pick<Storage, "getItem" | "setItem">;
  fetcher?: typeof fetch;
  force?: boolean;
} = {}) {
  const doc = options.doc || document;
  const locationRef = options.location || window.location;
  const storage = options.storage || window.sessionStorage;
  doc.documentElement.dataset.moonboxBuildId = BUILD_ID;

  const previousBuild = storage.getItem(BUILD_STORAGE_KEY);
  if (previousBuild !== BUILD_ID) storage.setItem(BUILD_STORAGE_KEY, BUILD_ID);
  if (!options.force && !import.meta.env.PROD) return false;

  const currentAssets = scriptAssetPaths(doc);
  if (!currentAssets.length) return false;
  const fetcher = options.fetcher || fetch;
  try {
    const response = await fetcher(locationRef.href, { cache: "no-store" });
    if (!response.ok) return false;
    const latestAssets = latestHtmlAssetPaths(await response.text(), locationRef.href);
    if (!latestAssets.length) return false;
    const isCurrent = currentAssets.some(asset => latestAssets.includes(asset));
    if (isCurrent) return false;
    const reloadTarget = `${BUILD_ID}:${latestAssets.join(",")}`;
    if (storage.getItem(RELOAD_STORAGE_KEY) === reloadTarget) return false;
    storage.setItem(RELOAD_STORAGE_KEY, reloadTarget);
    locationRef.reload();
    return true;
  } catch {
    return false;
  }
}
