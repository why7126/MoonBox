// 临时本地部署验收入口使用；不进入产品bundle，不读取或输出登录凭据。
(() => {
  history.replaceState(null, '', '/requirements');
  const records = [];
  const refreshState = {enabled_samples:0, disabled_samples:0};
  setInterval(() => { const button = [...document.querySelectorAll('button')].find(b=>b.textContent.trim()==='刷新需求中心' || b.getAttribute('aria-label')==='刷新需求中心'); if(button) refreshState[button.disabled?'disabled_samples':'enabled_samples']++; const el=document.getElementById('bug0016-refresh-state'); if(el)el.textContent=JSON.stringify(refreshState); },100);
  const render = () => {
    if (!document.body) return;
    let root = document.getElementById('bug0016-observer');
    if (!root) {
      root = document.createElement('details'); root.id = 'bug0016-observer';
      root.style.cssText = 'position:fixed;left:8px;bottom:8px;z-index:2000;max-width:600px;max-height:180px;overflow:auto;background:#fff;color:#111;padding:8px;font:11px monospace;border:1px solid #888';
      root.innerHTML = '<summary>本地读取验收（仅耗时与请求编号）</summary><pre id="bug0016-observation"></pre><pre id="bug0016-refresh-state"></pre>';
      document.body.appendChild(root);
    }
    document.getElementById('bug0016-observation').textContent = JSON.stringify(records.map(({url,start,...safe})=>safe));
  };
  const original = window.fetch.bind(window);
  window.fetch = async (...args) => {
    const url = new URL(typeof args[0] === 'string' ? args[0] : args[0].url, location.href);
    const operation = url.pathname.endsWith('/context') ? 'context' : url.pathname.includes('/documents/') ? (url.pathname.includes('/changes/') ? 'change_document' : 'issue_document') : null;
    if (!operation || !url.pathname.startsWith('/api/v1/requirement-center/')) return original(...args);
    const start = performance.now();
    const response = await original(...args);
    records.push({url:url.href,start,operation,status:response.status,headers_ms:Math.round(performance.now()-start),request_id:response.headers.get('X-Request-ID'),server_timing:response.headers.get('Server-Timing')});
    if(records.length>500)records.shift();render();return response;
  };
  new PerformanceObserver(list => {
    for (const e of list.getEntries()) {
      const record = records.findLast(r=>r.url===e.name && Math.abs(r.start-e.startTime)<100);
      if(record){record.ttfb_ms=Math.round(e.responseStart-e.requestStart);record.total_ms=Math.round(e.duration);}
    }
    render();
  }).observe({type:'resource',buffered:true});
})();
