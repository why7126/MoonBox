// Real React components with synthetic API responses; not deployed observation.
const fs = require('node:fs'), ts = require('typescript');
for (const ext of ['.ts','.tsx']) require.extensions[ext]=(module,filename)=>module._compile(ts.transpileModule(fs.readFileSync(filename,'utf8').replaceAll('import.meta.env','({})'),{compilerOptions:{target:ts.ScriptTarget.ES2020,module:ts.ModuleKind.CommonJS,jsx:ts.JsxEmit.ReactJSX,esModuleInterop:true},fileName:filename}).outputText,filename);
require.extensions['.css'] = () => {}; // DOM tests do not validate CSS.
const {JSDOM}=require('jsdom'),dom=new JSDOM('<html><body></body></html>',{url:'http://localhost'});
Object.assign(global,{window:dom.window,document:dom.window.document,HTMLElement:dom.window.HTMLElement,localStorage:dom.window.localStorage,requestAnimationFrame:fn=>setTimeout(fn,0)});
Object.defineProperty(global,'navigator',{value:dom.window.navigator,configurable:true});
const React=require('react'),{render,screen,cleanup,act,fireEvent,waitFor}=require('@testing-library/react');
const assert=require('node:assert/strict'),{test,afterEach}=require('node:test');
const {useConversationMessages}=require('../src/components/chat/useConversationMessages.ts');
const {ConversationMessages}=require('../src/components/chat/ConversationMessages.tsx');
const originalTimeout=global.setTimeout,originalClear=global.clearTimeout,originalFetch=global.fetch;
let queue=[],requests=[];
function setup(responder){
 queue=[];requests=[];localStorage.setItem('moonbox.session',JSON.stringify({access_token:'synthetic'}));
 global.setTimeout=(fn,ms,...args)=>{if(ms===3000||ms===250){const token={fn,args};queue.push(token);return token;}return originalTimeout(fn,ms,...args);};
 global.clearTimeout=token=>{if(typeof token==='object'&&token?.fn)queue=queue.filter(x=>x!==token);else originalClear(token);};
 global.fetch=async url=>{
  if(String(url).includes('/messages?')){requests.push(String(url));return new Response(JSON.stringify({code:0,data:await responder(String(url))}));}
  if(String(url).includes('/events'))return new Response('',{headers:{'Content-Type':'text/event-stream'}});
  return new Response(JSON.stringify({code:0,data:{id:'t',status:'stopped'}}));
 };
}
afterEach(()=>{cleanup();global.setTimeout=originalTimeout;global.clearTimeout=originalClear;global.fetch=originalFetch;localStorage.clear();});
async function step(){await act(async()=>{const item=queue.shift();assert.ok(item,'scheduled request');await item.fn(...item.args);});}
function message(tid,role,content=`${tid}-${role}`){const id=`${tid}-${role}`;return {id,turn_id:tid,role,content,created_at:role==='user'?'2026-10-21T00:00:08+00:00':'2026-10-21T00:00:00+00:00',display_time:null,time_source:role==='assistant'?'legacy_unknown':'message_saved',order_key:{turn_created_at:'2026-10-21T00:00:00+00:00',turn_id:tid,role_rank:role==='user'?0:1,message_id:id}};}
function Harness({cid='c'}){const {rows,loading,loadOlder,error}=useConversationMessages(cid,()=>()=>{});return React.createElement('div',null,React.createElement('button',{onClick:loadOlder,disabled:loading},'older'),React.createElement('output',null,rows.map(x=>x.content).join('|')),React.createElement('span',null,error));}
async function ready(text){await waitFor(()=>assert.equal(document.querySelector('output')?.textContent,text));}

test('actual component: cross-second user first and explicit unknown time',async()=>{
 setup(()=>({items:[message('t','assistant'),message('t','user')],has_more:false,next_cursor:null}));
 render(React.createElement(ConversationMessages,{conversationId:'c'}));await screen.findByText('t-user');
 assert.equal(document.querySelectorAll('.chat-message-block')[0].classList.contains('turn-user'),true);
 assert.ok(screen.getByText('历史回复时间未确认'));
});
test('cursor load, repeated pages and late output converge without duplication',async()=>{
 let late=false;
 setup(url=>url.includes('before=old')?{items:[message('a','user')],has_more:false,next_cursor:null}:{items:[...(late?[message('b','assistant')]:[]),message('b','user')],has_more:true,next_cursor:'old'});
 render(React.createElement(Harness));await ready('b-user');fireEvent.click(screen.getByText('older'));await ready('a-user|b-user');
 late=true;await step();await step();await ready('a-user|b-user|b-assistant');await step();await ready('a-user|b-user|b-assistant');
 assert.ok(requests.some(x=>x.includes('before=old')));
});
test('virtual to final body retains identity and position',async()=>{
 let final=false;setup(()=>({items:[{...message('a','assistant',final?'final':'partial'),output_source:final?'message':'events'},message('a','user')],has_more:false,next_cursor:null}));
 render(React.createElement(Harness));await ready('a-user|partial');final=true;await step();await ready('a-user|final');
 assert.equal(document.querySelector('output').textContent.split('|').length,2);
});
test('old conversation late response is discarded',async()=>{
 let release;setup(url=>url.includes('/old/')?new Promise(resolve=>{release=resolve;}):{items:[message('new','user')],has_more:false,next_cursor:null});
 const view=render(React.createElement(Harness,{cid:'old'}));await waitFor(()=>assert.ok(release));view.rerender(React.createElement(Harness,{cid:'new'}));await ready('new-user');
 await act(async()=>release({items:[message('old','user')],has_more:false,next_cursor:null}));await ready('new-user');
});
test('deep reconciliation is sequential, bounded and not restarted by polling',async()=>{
 let active=0,maxActive=0,version=0;
 setup(async url=>{active++;maxActive=Math.max(maxActive,active);await new Promise(resolve=>originalTimeout(resolve,2));active--;const page=url.includes('before=two')?2:url.includes('before=one')?1:0;return {items:[message(String(3-page),'user',`${3-page}-v${version}`)],has_more:page<2,next_cursor:page<2?(page===0?'one':'two'):null};});
 render(React.createElement(Harness));await ready('3-v0');fireEvent.click(screen.getByText('older'));await ready('2-v0|3-v0');fireEvent.click(screen.getByText('older'));await ready('1-v0|2-v0|3-v0');
 version=1;const before=requests.length;await step();await step();await step();await ready('1-v1|2-v1|3-v1');assert.equal(requests.length-before,3);assert.equal(maxActive,1);await step();assert.equal(requests.length-before,4);
});

test('unchanged newest page still discovers output in an older loaded turn',async()=>{
 let late=false,clock=100000;const originalNow=Date.now;Date.now=()=>clock;
 try {
  setup(url=>url.includes('before=one')?{items:[...(late?[message('a','assistant')]:[]),message('a','user')],has_more:false,next_cursor:null}:{items:[message('b','user')],has_more:true,next_cursor:'one'});
  render(React.createElement(Harness));await ready('b-user');fireEvent.click(screen.getByText('older'));await ready('a-user|b-user');
  await step();await step(); // Complete the first range review.
  late=true;clock+=16000;await step();await step();await ready('a-user|a-assistant|b-user');
 } finally {Date.now=originalNow;}
});
test('refresh remount keeps causal order and final text',async()=>{
 setup(()=>({items:[message('t','assistant','saved'),message('t','user')],has_more:false,next_cursor:null}));
 const first=render(React.createElement(Harness));await ready('t-user|saved');first.unmount();
 render(React.createElement(Harness));await ready('t-user|saved');
});
