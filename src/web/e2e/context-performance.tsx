import React from 'react';
import {createRoot} from 'react-dom/client';
import {RequirementCenterPage} from '../src/pages/catalog/RequirementCenterPage';
import '../src/styles/globals.css';
import '../src/styles/workbench.css';

// Test-only observation around the real page, with real HTTP and no data mocks.
// Timing starts at navigation, so module loading and render are included.
const evidence = document.getElementById('performance-evidence')!;
const params = new URLSearchParams(location.search);
const live = params.get('live') === '1';
const expectedCards = Number(params.get('cards') || '28');
const root = createRoot(document.getElementById('root')!);
let contextEvidence: {request_id: string | null; server_timing: string | null; status: number} | undefined;
const originalFetch = window.fetch.bind(window);
const refreshEvidence = document.createElement('output');
refreshEvidence.id = 'refresh-evidence';
refreshEvidence.style.cssText = 'position:fixed;bottom:20px;left:0;font-size:9px;max-width:75vw;max-height:40px;overflow:auto';
document.body.append(refreshEvidence);
const refreshSamples: unknown[] = [];
new PerformanceObserver(list => {
  for (const entry of list.getEntries()) {
    if (!entry.name.includes('/requirement-center/context?') || evidence.dataset.ready !== 'true' || refreshSamples.length >= 30) continue;
    refreshSamples.push({context_ms: entry.duration, ...contextEvidence});
    refreshEvidence.textContent = JSON.stringify(refreshSamples);
    refreshEvidence.dataset.ready = String(refreshSamples.length === 30);
  }
}).observe({type: 'resource', buffered: true});
window.fetch = async (...args: Parameters<typeof fetch>) => {
  const response = await originalFetch(...args);
  if (String(args[0]).includes('/requirement-center/context?')) {
    contextEvidence = {request_id: response.headers.get('X-Request-ID'),
      server_timing: response.headers.get('Server-Timing'), status: response.status};
  }
  return response;
};
document.getElementById('reset-caches')!.addEventListener('click', async event => {
  if (live) return; // Real deployments expose no test cache-reset/write routes.
  const button = event.currentTarget as HTMLButtonElement;
  button.dataset.ready = 'false';
  root.unmount(); // Stop the old page's polling before resetting caches.
  await fetch('/api/fixture/context/reset', {method: 'POST'});
  button.dataset.ready = 'true';
});
if (live) (document.getElementById('reset-caches') as HTMLButtonElement).disabled = true;
const observer = new MutationObserver(() => {
  const cards = document.querySelectorAll<HTMLElement>('.rc-card[data-issue-id]');
  // Use the recorded frozen fixture count; wait for the default-filter effect
  // rather than accepting transient unfiltered cards as the target view.
  if (cards.length !== expectedCards) return;
  const bounds = cards[0].getBoundingClientRect();
  if (!bounds.width || !bounds.height || bounds.bottom <= 0 || bounds.right <= 0 ||
      bounds.top >= window.innerHeight || bounds.left >= window.innerWidth) return;
  requestAnimationFrame(() => requestAnimationFrame(() => {
    const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];
    const context = resources.find(r => r.name.includes('/requirement-center/context?'));
    evidence.textContent = JSON.stringify({
      first_card_ms: performance.now(), visible_cards: document.querySelectorAll('.rc-card[data-issue-id]').length,
      context_ms: context?.duration, cold: params.get('cold') === '1',
      first_card_in_viewport: true, viewport_width: window.innerWidth, viewport_height: window.innerHeight,
      os_page_cache_cleared: false, ...contextEvidence,
    });
    evidence.dataset.ready = 'true';
    if (!live) void fetch('/api/fixture/context/measurement', {method: 'POST', keepalive: true,
      headers: {'Content-Type': 'application/json'}, body: evidence.textContent});
  }));
  observer.disconnect();
});
observer.observe(document.getElementById('root')!, {childList: true, subtree: true});
root.render(<RequirementCenterPage/>);
