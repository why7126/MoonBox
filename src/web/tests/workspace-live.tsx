import {createRoot} from 'react-dom/client';
import {useEffect, useState} from 'react';
import {WorkspacePanel} from '../src/components/workspaces/WorkspacePanel';
import '../src/styles/globals.css';
import '../src/styles/chat-workbench.css';
function Harness() {
  const [cid, setCid] = useState<string>();
  const [opened, setOpened] = useState(true);
  const theme = new URLSearchParams(location.search).get('theme') === 'dark' ? 'dark' : 'light';
  useEffect(() => { void fetch('/api/v1/workspace-test/context').then(value => value.json()).then(value => setCid(value.conversation_id)); }, []);
  return <main className={`requirement-center theme-${theme}`} data-theme={theme} style={{minHeight:'100vh',padding:24,display:'block'}}><p>合成验收样本 · 真实 API / Git / SQLite · 无模型调用</p><button style={{padding:12}} onClick={() => setOpened(true)}>打开工作区</button>{opened && cid && <WorkspacePanel spaceId={new URLSearchParams(location.search).get('scenario') === 'forbidden' ? 'denied-space' : 'space'} repositoryId={new URLSearchParams(location.search).get('scenario') === 'error' ? 'unconfigured-repo' : 'repo'} conversationId={cid} onClose={() => setOpened(false)} />}</main>;
}
createRoot(document.getElementById('root')!).render(<Harness />);
