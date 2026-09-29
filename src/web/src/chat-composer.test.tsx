import { cleanup,fireEvent,render,screen,waitFor } from '@testing-library/react';
import { afterEach,expect,it,vi } from 'vitest';
import { Composer } from './components/chat/Composer';
import type { Capabilities, ConversationRead } from './components/chat/chatApi';
afterEach(()=>{cleanup();vi.unstubAllGlobals();localStorage.clear();});
function typePrompt(value:string){
 const input=screen.getByTestId('chat-prompt');
 input.textContent=value;
 fireEvent.input(input);
 return input;
}
it('keeps the draft and request identity after an uncertain failure',async()=>{
 localStorage.setItem('moonbox.session',JSON.stringify({access_token:'synthetic'}));
 let first=true;
 vi.stubGlobal('fetch',vi.fn(async()=>{if(first){first=false;throw Error('连接中断');}return new Response(JSON.stringify({code:0,data:{id:'turn'}}));}));
 const submit=vi.fn(),draft=vi.fn();
 render(<Composer conversation={{id:'c'} as ConversationRead} capabilities={{execution_ready:true,reason:'',repositories:[],materials:{max_images:5,max_image_bytes:1000000,max_total_image_bytes:5000000,allowed_image_mime_types:['image/png'],max_skills:5,max_skill_summary_chars:1200,max_prompt_chars:32000}}} initialDraft="" onDraft={draft} onSubmitted={submit}/>);
 typePrompt('合成输入');fireEvent.click(screen.getByTestId('chat-send'));
 await screen.findByRole('alert');expect(screen.getByTestId('chat-prompt').textContent).toBe('合成输入');
 fireEvent.click(screen.getByTestId('chat-send'));await waitFor(()=>expect(submit).toHaveBeenCalledOnce());
 const calls=vi.mocked(fetch).mock.calls;expect(calls[0][1]?.body).toBe(calls[1][1]?.body);
 expect(screen.getByTestId('chat-prompt').textContent).toBe('');
});
it('sends Enter once and leaves Shift Enter and IME composition to the editor',async()=>{
 localStorage.setItem('moonbox.session',JSON.stringify({access_token:'synthetic'}));
 vi.stubGlobal('fetch',vi.fn(async()=>new Response(JSON.stringify({code:0,data:{id:'turn'}}))));
 render(<Composer conversation={{id:'c'} as ConversationRead} capabilities={{execution_ready:true,reason:'',repositories:[],materials:{max_images:5,max_image_bytes:1000000,max_total_image_bytes:5000000,allowed_image_mime_types:['image/png'],max_skills:5,max_skill_summary_chars:1200,max_prompt_chars:32000}}} initialDraft="测试" onDraft={()=>{}} onSubmitted={()=>{}}/>);
 const input=screen.getByTestId('chat-prompt');fireEvent.keyDown(input,{key:'Enter',shiftKey:true});fireEvent.keyDown(input,{key:'Enter',isComposing:true,keyCode:229});expect(fetch).not.toHaveBeenCalled();fireEvent.keyDown(input,{key:'Enter'});await waitFor(()=>expect(fetch).toHaveBeenCalledOnce());
});

it.each(['create','turn'])('retries a lost %s response without changing identities or losing the draft',async(failure)=>{
 localStorage.setItem('moonbox.session',JSON.stringify({access_token:'synthetic'}));
 let failed=false;const calls:{path:string;body:any}[]=[];
 vi.stubGlobal('fetch',vi.fn(async(url,options)=>{const path=String(url);calls.push({path,body:JSON.parse(options.body)});if(!failed && (failure==='create' ? path.endsWith('/conversations') : path.endsWith('/turns'))){failed=true;throw Error('响应丢失');}return new Response(JSON.stringify({code:0,data:path.endsWith('/conversations')?{id:'created',space_id:'space',repository_id:'repo'}:{id:'turn'}}));}));
 const created=vi.fn();render(<Composer spaceId="space" conversation={null} capabilities={{execution_ready:true,reason:'',repositories:[{id:'repo',space_id:'space'}],materials:{max_images:5,max_image_bytes:1000000,max_total_image_bytes:5000000,allowed_image_mime_types:['image/png'],max_skills:5,max_skill_summary_chars:1200,max_prompt_chars:32000}}} initialDraft="直接发送" onDraft={()=>{}} onSubmitted={()=>{}} onCreated={created}/>);
 expect(fetch).not.toHaveBeenCalled();fireEvent.click(screen.getByTestId('chat-send'));fireEvent.click(screen.getByTestId('chat-send'));
 await screen.findByRole('alert');expect(screen.getByTestId('chat-prompt').textContent).toBe('直接发送');
 fireEvent.click(screen.getByTestId('chat-send'));await waitFor(()=>expect(created).toHaveBeenCalledOnce());
 const creates=calls.filter(c=>c.path.endsWith('/conversations')),turns=calls.filter(c=>c.path.endsWith('/turns'));
 expect(creates).toHaveLength(failure==='create'?2:1);expect(turns).toHaveLength(failure==='turn'?2:1);
 expect(new Set(creates.map(c=>c.body.client_request_id)).size).toBe(1);expect(new Set(turns.map(c=>c.body.client_request_id)).size).toBe(1);
 expect(creates[0].body).toMatchObject({space_id:'space',repository_id:'repo'});
});
it('auto-selects the bound repository while permitting offline drafting',()=>{
 const props={spaceId:'space',conversation:null,initialDraft:'草稿',onDraft:vi.fn(),onSubmitted:vi.fn(),onCreated:vi.fn()};
 const repositories=[{id:'one',space_id:'space'},{id:'two',space_id:'space'}];
 const view=render(<Composer {...props} capabilities={{execution_ready:false,reason:'未就绪',repositories}}/>);
 expect(screen.getByTestId('chat-prompt').getAttribute('contenteditable')).toBe('true');
 view.rerender(<Composer {...props} capabilities={{execution_ready:true,reason:'',repositories}}/>);
 expect((screen.getByTestId('chat-send') as HTMLButtonElement).disabled).toBe(false);
 expect(screen.queryByLabelText('会话仓库')).toBeNull();
 expect(screen.getByTestId('chat-composer').getAttribute('data-repository')).toBe('one');
});

it('omits normal guidance and only describes actionable states',()=>{
 const props={conversation:{id:'c'} as ConversationRead,initialDraft:'草稿',onDraft:vi.fn(),onSubmitted:vi.fn()};
 const ready={execution_ready:true,reason:'',repositories:[],materials:{max_images:5,max_image_bytes:1000000,max_total_image_bytes:5000000,allowed_image_mime_types:['image/png'],max_skills:5,max_skill_summary_chars:1200,max_prompt_chars:32000}};
 const view=render(<Composer {...props} capabilities={ready}/>);
 expect(document.getElementById('chat-composer-hint')).toBeNull();
 expect(screen.getByTestId('chat-prompt').hasAttribute('aria-describedby')).toBe(false);
 const cases: Array<[ConversationRead | null, Capabilities, string]> = [
  [props.conversation,{...ready,execution_ready:false},'执行服务未就绪 · 可先编写草稿'],
  [{...props.conversation,archived:true},ready,'已归档 · 只读'],
  [{...props.conversation,active_turn_id:'t'},ready,'原运行尚未终止 · 可先编写草稿'],
  [null,{...ready,repositories:[]},'请选择本次对话使用的仓库'],
 ];
 for(const [conversation,capabilities,message] of cases){
  view.rerender(<Composer {...props} conversation={conversation} capabilities={capabilities}/>);
  expect(screen.getByText(message)).toBeTruthy();
  expect(screen.getByTestId('chat-prompt').getAttribute('aria-describedby')).toBe('chat-composer-hint');
 }
 view.rerender(<Composer {...props} capabilities={ready} unavailableReason="权限校验失败"/>);
 expect(screen.getByText('权限校验失败')).toBeTruthy();
});

it('shows conversation write scope separately from actionable composer hints',()=>{
 const ready={execution_ready:true,reason:'',repositories:[],materials:{max_images:5,max_image_bytes:1000000,max_total_image_bytes:5000000,allowed_image_mime_types:['image/png'],max_skills:5,max_skill_summary_chars:1200,max_prompt_chars:32000}};
 const props={initialDraft:'草稿',onDraft:vi.fn(),onSubmitted:vi.fn()};
	 const view=render(<Composer {...props} conversation={{id:'c',write_scope:'governance_write',write_reason_code:'governance_object_writable'} as ConversationRead} capabilities={ready}/>);
	 expect(screen.getByTestId('chat-write-scope').textContent).toBe('治理可写');
	 expect(screen.getByTestId('chat-write-scope').getAttribute('title')).toContain('治理文档写入');
	 expect(document.getElementById('chat-composer-hint')).toBeNull();
	 view.rerender(<Composer {...props} conversation={{id:'c',write_scope:'read_only',write_reason_code:'primary_object_required'} as ConversationRead} capabilities={ready}/>);
	 expect(screen.getByTestId('chat-write-scope').textContent).toBe('完全只读');
	 expect(screen.getByTestId('chat-write-scope').getAttribute('title')).toContain('管理关联');
	 expect(screen.getByTestId('chat-write-scope').getAttribute('aria-label')).toContain('设置主对象');
	});

it('sends an image-only turn with a sanitized reference',async()=>{
 localStorage.setItem('moonbox.session',JSON.stringify({access_token:'synthetic'}));
 const calls:{path:string;body:any}[]=[];
 vi.stubGlobal('fetch',vi.fn(async(url,options)=>{const path=String(url);calls.push({path,body:options?.body instanceof FormData ? 'form-data' : JSON.parse(String(options?.body))});if(path.includes('/materials'))return new Response(JSON.stringify({code:0,data:{ref_id:'mat1',kind:'image',name:'shot.png',mime_type:'image/png',size_bytes:4,status:'ready'}}));return new Response(JSON.stringify({code:0,data:{id:'turn'}}));}));
 render(<Composer conversation={{id:'c',space_id:'space',repository_id:'repo'} as ConversationRead} capabilities={{execution_ready:true,reason:'',repositories:[],materials:{max_images:5,max_image_bytes:1000000,max_total_image_bytes:5000000,allowed_image_mime_types:['image/png'],allowed_file_mime_types:['image/png','application/pdf'],max_files:8,max_file_bytes:1000000,max_total_file_bytes:5000000,max_skills:5,max_skill_summary_chars:1200,max_prompt_chars:32000}}} initialDraft="" onDraft={()=>{}} onSubmitted={()=>{}}/>);
 const file=new File(['fake'],'shot.png',{type:'image/png'});
 fireEvent.change(screen.getByTestId('chat-file-input'),{target:{files:[file]}});
 expect(screen.getByTestId('chat-image-attachment').textContent).toContain('shot.png');
 await waitFor(()=>expect(calls.some(call=>call.path.includes('/materials'))).toBe(true));
 expect((screen.getByTestId('chat-send') as HTMLButtonElement).disabled).toBe(false);
 fireEvent.click(screen.getByTestId('chat-send'));
 await waitFor(()=>expect(calls.some(call=>call.path.endsWith('/turns'))).toBe(true));
 expect(calls.some(call=>call.body.event_name==='chat.image_add')).toBe(true);
 const turn = calls.find(call=>call.path.endsWith('/turns'))!;
 expect(turn.body.prompt).toBe('');
 expect(turn.body.attachments).toEqual([{ref_id:'mat1',kind:'image',name:'shot.png',mime_type:'image/png',size_bytes:4}]);
});

it('loads skill candidates and sends selected skill context',async()=>{
 localStorage.setItem('moonbox.session',JSON.stringify({access_token:'synthetic'}));
 const calls:{path:string;body?:any}[]=[];
 vi.stubGlobal('fetch',vi.fn(async(url,options)=>{const path=String(url);calls.push({path,body:options?.body?JSON.parse(String(options.body)):undefined});if(path.includes('/skills'))return new Response(JSON.stringify({code:0,data:{items:[
  {id:'bug-capture',name:'bug-capture',summary:'缺陷记录 - 轻量 capture，分配 BUG-ID',source:'.agents/skills/bug-capture/SKILL.md',digest:'bug',injection_scope:'context_reference_only'},
  {id:'req-explore',name:'req-explore',summary:'需求探索',source:'.agents/skills/req-explore/SKILL.md',digest:'req',injection_scope:'context_reference_only'}
 ]}}));return new Response(JSON.stringify({code:0,data:{id:'turn'}}));}));
 render(<Composer conversation={{id:'c'} as ConversationRead} capabilities={{execution_ready:true,reason:'',repositories:[],materials:{max_images:5,max_image_bytes:1000000,max_total_image_bytes:5000000,allowed_image_mime_types:['image/png'],max_skills:5,max_skill_summary_chars:1200,max_prompt_chars:32000}}} initialDraft="结合Skill" onDraft={()=>{}} onSubmitted={()=>{}}/>);
 const upload = screen.getByTestId('chat-file-input');
 const skill = screen.getByTestId('chat-skill-button');
 expect(upload.closest('.chat-material-actions')).toBe(skill.parentElement);
 typePrompt('结合 /bug');
 await screen.findByTestId('chat-skill-menu');
 expect(screen.getByText('Bug Capture')).toBeTruthy();
 expect(screen.queryByText('Req Explore')).toBeNull();
 expect(screen.getByText('缺陷记录 - 轻量 capture，分配 BUG-ID')).toBeTruthy();
 expect(screen.queryByText('---')).toBeNull();
 fireEvent.click(screen.getByText('Bug Capture'));
 const token = screen.getByTestId('chat-skill-token');
 const inputRow = screen.getByTestId('chat-input-row');
 const richComposer = screen.getByTestId('chat-rich-composer');
 expect(token.textContent).toContain('Bug Capture');
 expect(token.textContent).not.toContain('context_reference_only');
 expect(token.className).toContain('chat-skill-token-inline');
 expect(inputRow.querySelector('[data-testid="chat-skill-token"]')).toBe(token);
 expect(richComposer.querySelector('[data-testid="chat-skill-token"]')).toBe(token);
 expect(richComposer.querySelector('[data-testid="chat-prompt"]')?.textContent).toBe('结合 ');
 expect(screen.queryByTestId('chat-attachment-strip')).toBeNull();
 fireEvent.click(screen.getByTestId('chat-send'));
 await waitFor(()=>expect(calls.some(call=>call.path.endsWith('/turns'))).toBe(true));
 expect(calls.some(call=>call.body?.event_name==='chat.skill_select')).toBe(true);
 const turn= calls.find(call=>call.path.endsWith('/turns'))!;
 expect(turn.body.skills[0]).toMatchObject({id:'bug-capture',digest:'bug'});
});

it('supports keyboard navigation in the skill menu',async()=>{
 localStorage.setItem('moonbox.session',JSON.stringify({access_token:'synthetic'}));
 vi.stubGlobal('fetch',vi.fn(async(url)=>{const path=String(url);if(path.includes('/skills'))return new Response(JSON.stringify({code:0,data:{items:[
  {id:'bug-explore',name:'bug-explore',summary:'缺陷探索',source:'.agents/skills/bug-explore/SKILL.md',digest:'bug-explore',injection_scope:'context_reference_only'},
  {id:'explore',name:'explore',summary:'通用探索模式',source:'.agents/skills/explore/SKILL.md',digest:'explore',injection_scope:'context_reference_only'},
  {id:'opsx-explore',name:'opsx-explore',summary:'OpenSpec探索',source:'.agents/skills/opsx-explore/SKILL.md',digest:'opsx-explore',injection_scope:'context_reference_only'}
 ]}}));return new Response(JSON.stringify({code:0,data:{id:'turn'}}));}));
 render(<Composer conversation={{id:'c'} as ConversationRead} capabilities={{execution_ready:true,reason:'',repositories:[],materials:{max_images:5,max_image_bytes:1000000,max_total_image_bytes:5000000,allowed_image_mime_types:['image/png'],max_skills:5,max_skill_summary_chars:1200,max_prompt_chars:32000}}} initialDraft="" onDraft={()=>{}} onSubmitted={()=>{}}/>);
 const input=typePrompt('/ex');
 await screen.findByTestId('chat-skill-menu');
 expect(screen.getByRole('option',{selected:true}).textContent).toContain('Bug Explore');
 fireEvent.keyDown(input,{key:'ArrowDown'});
 expect(screen.getByRole('option',{selected:true}).textContent).toContain('Explore');
 fireEvent.keyDown(input,{key:'Enter'});
 expect(screen.queryByTestId('chat-skill-menu')).toBeNull();
 expect(screen.getByTestId('chat-skill-token').textContent).toContain('Explore');
 typePrompt('/ex');
 await screen.findByTestId('chat-skill-menu');
 fireEvent.keyDown(input,{key:'Escape'});
 expect(screen.queryByTestId('chat-skill-menu')).toBeNull();
});

it('closes only slash-triggered skill menus when the slash query is removed',async()=>{
 localStorage.setItem('moonbox.session',JSON.stringify({access_token:'synthetic'}));
 vi.stubGlobal('fetch',vi.fn(async(url)=>{const path=String(url);if(path.includes('/skills'))return new Response(JSON.stringify({code:0,data:{items:[
  {id:'explore',name:'explore',summary:'通用探索模式',source:'.agents/skills/explore/SKILL.md',digest:'explore',injection_scope:'context_reference_only'}
 ]}}));return new Response(JSON.stringify({code:0,data:{id:'turn'}}));}));
 render(<Composer conversation={{id:'c'} as ConversationRead} capabilities={{execution_ready:true,reason:'',repositories:[],materials:{max_images:5,max_image_bytes:1000000,max_total_image_bytes:5000000,allowed_image_mime_types:['image/png'],max_skills:5,max_skill_summary_chars:1200,max_prompt_chars:32000}}} initialDraft="" onDraft={()=>{}} onSubmitted={()=>{}}/>);
 const input=typePrompt('/ex');
 await screen.findByTestId('chat-skill-menu');
 typePrompt('');
 expect(screen.queryByTestId('chat-skill-menu')).toBeNull();
 fireEvent.click(screen.getByTestId('chat-skill-button'));
 await screen.findByTestId('chat-skill-menu');
 typePrompt('普通输入');
 expect(screen.getByTestId('chat-skill-menu')).toBeTruthy();
 fireEvent.keyDown(input,{key:'Escape'});
 expect(screen.queryByTestId('chat-skill-menu')).toBeNull();
});

it('uses one popover behavior for skill model and reasoning menus',async()=>{
 localStorage.setItem('moonbox.session',JSON.stringify({access_token:'synthetic'}));
 vi.stubGlobal('fetch',vi.fn(async(url)=>{const path=String(url);if(path.includes('/skills'))return new Response(JSON.stringify({code:0,data:{items:[
  {id:'explore',name:'explore',summary:'通用探索模式',source:'.agents/skills/explore/SKILL.md',digest:'explore',injection_scope:'context_reference_only'}
 ]}}));return new Response(JSON.stringify({code:0,data:{id:'turn'}}));}));
 const capabilities={
  execution_ready:true,reason:'',repositories:[],materials:{max_images:5,max_image_bytes:1000000,max_total_image_bytes:5000000,allowed_image_mime_types:['image/png'],max_skills:5,max_skill_summary_chars:1200,max_prompt_chars:32000},
  execution:{policy_version:'chat-execution-config-v1',agents:[{value:'codex',display_name:'Codex',available:true}],models:[{value:'gpt-6-astra',display_name:'GPT-6 Astra',available:true},{value:'gpt-5.6-sol',display_name:'GPT-5.6 Sol',available:true}],reasoning:[{value:'high',display_name:'High',available:true},{value:'medium',display_name:'Medium',available:true}],defaults:{agent:'codex',model:'gpt-6-astra',reasoning:'high'}}
 } satisfies Capabilities;
 render(<Composer conversation={{id:'c'} as ConversationRead} capabilities={capabilities} initialDraft="" onDraft={()=>{}} onSubmitted={()=>{}}/>);
 fireEvent.click(screen.getByTestId('chat-skill-button'));
 const skillMenu=await screen.findByTestId('chat-skill-menu');
 expect(skillMenu.className).toContain('chat-composer-popover');
 expect(screen.getByRole('option',{name:/Explore/}).className).toContain('chat-composer-option');
 fireEvent.mouseDown(screen.getByTestId('chat-input-row'));
 expect(screen.queryByTestId('chat-skill-menu')).toBeNull();
 fireEvent.click(screen.getByTestId('chat-skill-button'));
 await screen.findByTestId('chat-skill-menu');
 fireEvent.click(screen.getByTestId('chat-model-selector'));
 expect(screen.queryByTestId('chat-skill-menu')).toBeNull();
 const modelMenu=screen.getByTestId('chat-execution-config-menu');
 expect(modelMenu.className).toContain('chat-composer-popover');
 expect(screen.getByRole('menuitemradio',{name:'GPT-6 Astra'}).className).toContain('chat-composer-option');
 fireEvent.mouseDown(screen.getByTestId('chat-composer'));
 expect(screen.queryByTestId('chat-execution-config-menu')).toBeNull();
 fireEvent.click(screen.getByTestId('chat-model-selector'));
 expect(screen.getByTestId('chat-execution-config-menu')).toBeTruthy();
 fireEvent.keyDown(document,{key:'Escape'});
 expect(screen.queryByTestId('chat-execution-config-menu')).toBeNull();
 fireEvent.click(screen.getByTestId('chat-model-selector'));
 fireEvent.click(screen.getByTestId('chat-reasoning-selector'));
 const reasoningMenu=screen.getByTestId('chat-execution-config-menu');
 expect(screen.getByRole('menuitemradio',{name:'High'}).className).toContain('chat-composer-option');
 expect(reasoningMenu.textContent).not.toContain('GPT-6 Astra');
 fireEvent.mouseDown(screen.getByTestId('chat-input-row'));
 expect(screen.queryByTestId('chat-execution-config-menu')).toBeNull();
 fireEvent.click(screen.getByTestId('chat-reasoning-selector'));
 fireEvent.click(screen.getByText('Medium'));
 expect(screen.queryByTestId('chat-execution-config-menu')).toBeNull();
});

it('removes a selected skill chip with Delete and keeps the send payload in sync',async()=>{
 localStorage.setItem('moonbox.session',JSON.stringify({access_token:'synthetic'}));
 const calls:{path:string;body?:any}[]=[];
 vi.stubGlobal('fetch',vi.fn(async(url,options)=>{const path=String(url);calls.push({path,body:options?.body?JSON.parse(String(options.body)):undefined});if(path.includes('/skills'))return new Response(JSON.stringify({code:0,data:{items:[
  {id:'bug-capture',name:'bug-capture',summary:'缺陷记录 - 轻量 capture，分配 BUG-ID',source:'.agents/skills/bug-capture/SKILL.md',digest:'bug',injection_scope:'context_reference_only'}
 ]}}));return new Response(JSON.stringify({code:0,data:{id:'turn'}}));}));
 render(<Composer conversation={{id:'c'} as ConversationRead} capabilities={{execution_ready:true,reason:'',repositories:[],materials:{max_images:5,max_image_bytes:1000000,max_total_image_bytes:5000000,allowed_image_mime_types:['image/png'],max_skills:5,max_skill_summary_chars:1200,max_prompt_chars:32000}}} initialDraft="" onDraft={()=>{}} onSubmitted={()=>{}}/>);
 typePrompt('/bug');
 await screen.findByTestId('chat-skill-menu');
 fireEvent.click(screen.getByText('Bug Capture'));
 const token = screen.getByTestId('chat-skill-token');
 token.focus();
 fireEvent.keyDown(token,{key:'Delete'});
 expect(screen.queryByTestId('chat-skill-token')).toBeNull();
 expect(calls.some(call=>call.body?.event_name==='chat.skill_remove')).toBe(true);
 typePrompt('修复布局');
 fireEvent.click(screen.getByTestId('chat-send'));
 await waitFor(()=>expect(calls.some(call=>call.path.endsWith('/turns'))).toBe(true));
 const turn= calls.find(call=>call.path.endsWith('/turns'))!;
 expect(turn.body.prompt).toBe('修复布局');
 expect(turn.body.skills).toEqual([]);
});

it('selects model and reasoning and sends the stable execution config',async()=>{
 localStorage.setItem('moonbox.session',JSON.stringify({access_token:'synthetic'}));
 const calls:{path:string;body?:any}[]=[];
 vi.stubGlobal('fetch',vi.fn(async(url,options)=>{calls.push({path:String(url),body:options?.body?JSON.parse(String(options.body)):undefined});return new Response(JSON.stringify({code:0,data:{id:'turn',effective_config:{agent:'codex',model:'gpt-5.6-sol',reasoning:'medium'}}}));}));
 const capabilities={
  execution_ready:true,reason:'',repositories:[],materials:{max_images:5,max_image_bytes:1000000,max_total_image_bytes:5000000,allowed_image_mime_types:['image/png'],max_skills:5,max_skill_summary_chars:1200,max_prompt_chars:32000},
  execution:{policy_version:'chat-execution-config-v1',agents:[{value:'codex',display_name:'Codex',available:true}],models:[{value:'gpt-6-astra',display_name:'GPT-6 Astra',available:true},{value:'gpt-5.6-sol',display_name:'GPT-5.6 Sol',available:true},{value:'gpt-5.6-terra',display_name:'GPT-5.6 Terra',available:true},{value:'gpt-5.6-luna',display_name:'GPT-5.6 Luna',available:true},{value:'gpt-5.5',display_name:'GPT-5.5',available:true},{value:'legacy',display_name:'legacy',available:false,disabled_reason:'已停用'}],reasoning:[{value:'high',display_name:'High',available:true},{value:'medium',display_name:'Medium',available:true}],defaults:{agent:'codex',model:'gpt-6-astra',reasoning:'high'}}
 };
 render(<Composer conversation={{id:'c'} as ConversationRead} capabilities={capabilities} initialDraft="选择配置" onDraft={()=>{}} onSubmitted={()=>{}}/>);
 expect(screen.getByTestId('chat-execution-config-bar').textContent).toContain('GPT-6 Astra');
 fireEvent.click(screen.getByTestId('chat-model-selector'));
 const modelItems=screen.getAllByRole('menuitemradio').map(item=>item.textContent);
 expect(modelItems.slice(0,5)).toEqual(['GPT-6 Astra','GPT-5.6 Sol','GPT-5.6 Terra','GPT-5.6 Luna','GPT-5.5']);
 expect(screen.getByText('GPT-5.6 Luna').textContent).toBe('GPT-5.6 Luna');
 expect(screen.getByText('GPT-5.5').textContent).toBe('GPT-5.5');
 expect((screen.getByTitle('已停用') as HTMLButtonElement).disabled).toBe(true);
 fireEvent.click(screen.getByText('GPT-5.6 Sol'));
 expect(screen.queryByTestId('chat-execution-config-menu')).toBeNull();
 fireEvent.click(screen.getByTestId('chat-reasoning-selector'));
 fireEvent.click(screen.getByText('Medium'));
 expect(screen.queryByTestId('chat-execution-config-menu')).toBeNull();
 fireEvent.click(screen.getByTestId('chat-send'));
 await waitFor(()=>expect(calls.some(call=>call.path.endsWith('/turns'))).toBe(true));
 expect(calls.filter(call=>call.body?.event_name==='chat.config_select')).toHaveLength(2);
 const turn=calls.find(call=>call.path.endsWith('/turns'))!;
 expect(turn.body.execution_config).toEqual({agent:'codex',model:'gpt-5.6-sol',reasoning:'medium'});
});
