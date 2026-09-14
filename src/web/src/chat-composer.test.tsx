import { cleanup,fireEvent,render,screen,waitFor } from '@testing-library/react';
import { afterEach,expect,it,vi } from 'vitest';
import { Composer } from './components/chat/Composer';
import type { ConversationRead } from './components/chat/chatApi';
afterEach(()=>{cleanup();vi.unstubAllGlobals();localStorage.clear();});
it('keeps the draft and request identity after an uncertain failure',async()=>{
 localStorage.setItem('moonbox.session',JSON.stringify({access_token:'synthetic'}));
 let first=true;
 vi.stubGlobal('fetch',vi.fn(async()=>{if(first){first=false;throw Error('连接中断');}return new Response(JSON.stringify({code:0,data:{id:'turn'}}));}));
 const submit=vi.fn(),draft=vi.fn();
 render(<Composer conversation={{id:'c'} as ConversationRead} capabilities={{execution_ready:true,reason:'',repositories:[]}} initialDraft="" onDraft={draft} onSubmitted={submit}/>);
 fireEvent.change(screen.getByTestId('chat-prompt'),{target:{value:'合成输入'}});fireEvent.click(screen.getByTestId('chat-send'));
 await screen.findByRole('alert');expect((screen.getByTestId('chat-prompt') as HTMLTextAreaElement).value).toBe('合成输入');
 fireEvent.click(screen.getByTestId('chat-send'));await waitFor(()=>expect(submit).toHaveBeenCalledOnce());
 const calls=vi.mocked(fetch).mock.calls;expect(calls[0][1]?.body).toBe(calls[1][1]?.body);
 expect((screen.getByTestId('chat-prompt') as HTMLTextAreaElement).value).toBe('');
});
it('sends Enter once and leaves Shift Enter and IME composition to the editor',async()=>{
 localStorage.setItem('moonbox.session',JSON.stringify({access_token:'synthetic'}));
 vi.stubGlobal('fetch',vi.fn(async()=>new Response(JSON.stringify({code:0,data:{id:'turn'}}))));
 render(<Composer conversation={{id:'c'} as ConversationRead} capabilities={{execution_ready:true,reason:'',repositories:[]}} initialDraft="测试" onDraft={()=>{}} onSubmitted={()=>{}}/>);
 const input=screen.getByTestId('chat-prompt');fireEvent.keyDown(input,{key:'Enter',shiftKey:true});fireEvent.keyDown(input,{key:'Enter',isComposing:true,keyCode:229});expect(fetch).not.toHaveBeenCalled();fireEvent.keyDown(input,{key:'Enter'});await waitFor(()=>expect(fetch).toHaveBeenCalledOnce());
});

it.each(['create','turn'])('retries a lost %s response without changing identities or losing the draft',async(failure)=>{
 localStorage.setItem('moonbox.session',JSON.stringify({access_token:'synthetic'}));
 let failed=false;const calls:{path:string;body:any}[]=[];
 vi.stubGlobal('fetch',vi.fn(async(url,options)=>{const path=String(url);calls.push({path,body:JSON.parse(options.body)});if(!failed && (failure==='create' ? path.endsWith('/conversations') : path.endsWith('/turns'))){failed=true;throw Error('响应丢失');}return new Response(JSON.stringify({code:0,data:path.endsWith('/conversations')?{id:'created',space_id:'space',repository_id:'repo'}:{id:'turn'}}));}));
 const created=vi.fn();render(<Composer spaceId="space" conversation={null} capabilities={{execution_ready:true,reason:'',repositories:[{id:'repo',space_id:'space'}]}} initialDraft="直接发送" onDraft={()=>{}} onSubmitted={()=>{}} onCreated={created}/>);
 expect(fetch).not.toHaveBeenCalled();fireEvent.click(screen.getByTestId('chat-send'));fireEvent.click(screen.getByTestId('chat-send'));
 await screen.findByRole('alert');expect((screen.getByTestId('chat-prompt') as HTMLTextAreaElement).value).toBe('直接发送');
 fireEvent.click(screen.getByTestId('chat-send'));await waitFor(()=>expect(created).toHaveBeenCalledOnce());
 const creates=calls.filter(c=>c.path.endsWith('/conversations')),turns=calls.filter(c=>c.path.endsWith('/turns'));
 expect(creates).toHaveLength(failure==='create'?2:1);expect(turns).toHaveLength(failure==='turn'?2:1);
 expect(new Set(creates.map(c=>c.body.client_request_id)).size).toBe(1);expect(new Set(turns.map(c=>c.body.client_request_id)).size).toBe(1);
 expect(creates[0].body).toMatchObject({space_id:'space',repository_id:'repo'});
});
it('requires inline selection for multiple repositories while permitting offline drafting',()=>{
 const props={spaceId:'space',conversation:null,initialDraft:'草稿',onDraft:vi.fn(),onSubmitted:vi.fn(),onCreated:vi.fn()};
 const repositories=[{id:'one',space_id:'space'},{id:'two',space_id:'space'}];
 const view=render(<Composer {...props} capabilities={{execution_ready:false,reason:'未就绪',repositories}}/>);
 expect((screen.getByTestId('chat-prompt') as HTMLTextAreaElement).disabled).toBe(false);
 view.rerender(<Composer {...props} capabilities={{execution_ready:true,reason:'',repositories}}/>);
 expect((screen.getByTestId('chat-send') as HTMLButtonElement).disabled).toBe(true);
 fireEvent.change(screen.getByLabelText('会话仓库'),{target:{value:'two'}});
 expect((screen.getByTestId('chat-send') as HTMLButtonElement).disabled).toBe(false);
});

it('omits normal guidance and only describes actionable states',()=>{
 const props={conversation:{id:'c'} as ConversationRead,initialDraft:'草稿',onDraft:vi.fn(),onSubmitted:vi.fn()};
 const ready={execution_ready:true,reason:'',repositories:[]};
 const view=render(<Composer {...props} capabilities={ready}/>);
 expect(document.getElementById('chat-composer-hint')).toBeNull();
 expect(screen.getByTestId('chat-prompt').hasAttribute('aria-describedby')).toBe(false);
 for(const [conversation,capabilities,message] of [
  [props.conversation,{...ready,execution_ready:false},'执行服务未就绪 · 可先编写草稿'],
  [{...props.conversation,archived:true},ready,'已归档 · 只读'],
  [{...props.conversation,active_turn_id:'t'},ready,'原运行尚未终止 · 可先编写草稿'],
  [null,ready,'请选择本次对话使用的仓库'],
 ] as const){
  view.rerender(<Composer {...props} conversation={conversation} capabilities={capabilities}/>);
  expect(screen.getByText(message)).toBeTruthy();
  expect(screen.getByTestId('chat-prompt').getAttribute('aria-describedby')).toBe('chat-composer-hint');
 }
 view.rerender(<Composer {...props} capabilities={ready} unavailableReason="权限校验失败"/>);
 expect(screen.getByText('权限校验失败')).toBeTruthy();
});
