import React from 'react';
import {createRoot} from 'react-dom/client';
import {WorkspaceOverview, type WorkspaceOverviewState} from '../src/components/workspaces/WorkspaceOverview';
import '../src/styles/globals.css';
const params = new URLSearchParams(location.search);
const theme = params.get('theme') === 'light' ? 'light' : 'dark';
const state = (params.get('state') || 'ready') as WorkspaceOverviewState;
createRoot(document.getElementById('root')!).render(<main className={`requirement-center workspace-skeleton-layout theme-${theme}`} data-theme={theme}>
  <style>{`.workspace-skeleton-layout{display:grid;grid-template-columns:216px minmax(0,1fr);min-height:100vh}@media(max-width:720px){.workspace-skeleton-layout{grid-template-columns:1fr}.workspace-skeleton-layout>aside{display:none}}`}</style>
  <aside style={{padding:24,borderRight:'1px solid var(--rc-border)'}}><strong>MoonBox</strong><p>骨架验证</p><p>合成数据 · 不调用 API</p></aside>
  <WorkspaceOverview state={state} items={[]} onReload={()=>{}} />
</main>);
