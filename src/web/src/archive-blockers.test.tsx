import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import { Composer, type DraftState } from './components/chat/Composer';
import type { ConversationRead } from './components/chat/chatApi';

afterEach(() => { cleanup(); vi.unstubAllGlobals(); });
it('rejected archive shows separate actionable blockers and retains text, materials and skills', async () => {
  const entries = new Map<string, string>();
  vi.stubGlobal('localStorage', {
    getItem: (key: string) => entries.get(key) ?? null,
    setItem: (key: string, value: string) => { entries.set(key, value); },
    removeItem: (key: string) => { entries.delete(key); },
    clear: () => { entries.clear(); },
  });
  localStorage.setItem('moonbox.session', JSON.stringify({access_token:'synthetic', username:'tester', started_at:new Date().toISOString()}));
  const fetch = vi.fn().mockResolvedValue({ok:false,status:409,json:async()=>({code:2509,message:'归档未就绪',data:{archive_blockers:[
    {type:'change',id:'fix-example',status:'archive_requirement_conflict',message:'原条文兼容证明缺失',action_hint:'核对原约束与新增场景',visible:true},
    {type:'acceptance_report',id:'sprint-099',status:'missing_signoff',message:'人工验收未签署',action_hint:'完成验收报告签署',visible:true}
  ]}})});
  vi.stubGlobal('fetch',fetch);
  const state: DraftState = {text:'/sprint-archive sprint-099', images:[{id:'file',ref_id:'ref',kind:'file',name:'summary.txt',mime_type:'text/plain',size_bytes:8,status:'done'}],skills:[{id:'skill',name:'review',summary:'审查',source:'project',digest:'digest',injection_scope:'turn'}]};
  const onSubmitted=vi.fn();
  render(<Composer conversation={{id:'conversation',repository_id:'repo',space_id:'space',archived:false} as ConversationRead} capabilities={{execution_ready:true,reason:'',repositories:[]}} initialDraft={state.text} draftState={state} onDraft={vi.fn()} onSubmitted={onSubmitted}/>);
  expect(fetch).not.toHaveBeenCalled();
  fireEvent.click(screen.getByTestId('chat-send'));
  await waitFor(()=>expect(screen.getAllByTestId('archive-blocker-item')).toHaveLength(2));
  expect(screen.getByTestId('chat-prompt').textContent).toBe(state.text);
  expect(screen.getByTestId('chat-file-attachment').textContent).toContain('summary.txt');
  expect(screen.getByTestId('chat-skill-token').textContent).toContain('Review');
  expect(screen.getByText('核对原约束与新增场景')).toBeTruthy();
  expect(screen.getByText('完成验收报告签署')).toBeTruthy();
  fireEvent.click(screen.getAllByText('查看处理步骤')[0]);
  expect(fetch).toHaveBeenCalledTimes(1);
  expect(onSubmitted).not.toHaveBeenCalled();
});
