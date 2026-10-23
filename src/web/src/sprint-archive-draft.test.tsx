import React from 'react';
import {render,screen,fireEvent,cleanup} from '@testing-library/react';
import {afterEach,expect,it,vi} from 'vitest';
import {SprintArchiveDraft} from './components/chat/SprintArchiveDraft';
afterEach(()=>{cleanup();vi.unstubAllGlobals();});
it('preserves by explicit keep or Escape and replaces only on explicit choice',()=>{
 const keep=vi.fn(),replace=vi.fn();
 render(<SprintArchiveDraft sprintId="sprint-099" onKeep={keep} onReplace={replace}/>);
 expect(keep).not.toHaveBeenCalled();expect(replace).not.toHaveBeenCalled();
 fireEvent.click(screen.getByTestId('sprint-archive-draft-keep'));expect(keep).toHaveBeenCalledTimes(1);
 fireEvent.keyDown(screen.getByTestId('sprint-archive-draft-conflict'),{key:'Escape'});expect(keep).toHaveBeenCalledTimes(2);
 fireEvent.click(screen.getByTestId('sprint-archive-draft-replace'));expect(replace).toHaveBeenCalledTimes(1);
});
it('does not allow replacement while unavailable',()=>{
 const replace=vi.fn();render(<SprintArchiveDraft sprintId="sprint-099" disabled onKeep={()=>{}} onReplace={replace}/>);
 fireEvent.click(screen.getByTestId('sprint-archive-draft-replace'));expect(replace).not.toHaveBeenCalled();
});

import {Composer,type DraftState} from './components/chat/Composer';
it('Composer remount for archive prefill retains existing material and skill context without a request',()=>{
 const fetch=vi.fn();vi.stubGlobal('fetch',fetch);
 const state:DraftState={text:'原草稿',images:[{id:'material',ref_id:'ref',kind:'file',name:'summary.txt',mime_type:'text/plain',size_bytes:8,status:'done'}],skills:[{id:'skill',name:'review',summary:'测试技能',source:'project',digest:'digest',injection_scope:'turn'}]};
 const props={spaceId:'space',conversation:null,capabilities:null,draftState:state,onDraft:vi.fn(),onSubmitted:vi.fn()};
 const view=render(<Composer key="before" {...props} initialDraft={state.text}/>);
 state.text='/sprint-archive sprint-099';state.hiddenPrompt=undefined;state.request=undefined;
 view.rerender(<Composer key="after" {...props} initialDraft={state.text}/>);
 expect(screen.getByTestId('chat-prompt').textContent).toBe('/sprint-archive sprint-099');
 expect(screen.getByTestId('chat-file-attachment').textContent).toContain('summary.txt');
 expect(screen.getByTestId('chat-skill-token').textContent).toContain('Review');
 expect(fetch).not.toHaveBeenCalled();vi.unstubAllGlobals();
});
