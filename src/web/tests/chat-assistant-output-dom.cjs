// Portable DOM fallback for hosts without native Vite dependencies; not a browser layout test.
const {createRequire}=require('node:module');
const req=createRequire(require('node:path').resolve(__dirname, '../package.json'));
const ts=req('typescript'),fs=require('node:fs'),assert=require('node:assert/strict');
const {JSDOM}=req('jsdom');
const dom=new JSDOM('<!doctype html><html><body></body></html>',{url:'http://localhost/chat',pretendToBeVisual:true});
for(const name of ['window','document','navigator','HTMLElement','Element','Node','MutationObserver','localStorage','getComputedStyle','requestAnimationFrame','cancelAnimationFrame'])Object.defineProperty(global,name,{configurable:true,value:typeof dom.window[name]==='function'&&['getComputedStyle','requestAnimationFrame','cancelAnimationFrame'].includes(name)?dom.window[name].bind(dom.window):dom.window[name]});
for(const ext of ['.ts','.tsx'])require.extensions[ext]=(mod,file)=>{const out=ts.transpileModule(fs.readFileSync(file,'utf8').replaceAll('import.meta.env', '{}'),{compilerOptions:{module:ts.ModuleKind.CommonJS,jsx:ts.JsxEmit.ReactJSX,target:ts.ScriptTarget.ES2022,esModuleInterop:true}});mod._compile(out.outputText,file);};
require.extensions['.css']=()=>{};
const React=req('react'),{render,screen,cleanup}=req('@testing-library/react');
const {ConversationMessages}=req('./src/components/chat/ConversationMessages.tsx');
(async()=>{
for(const status of ['unknown','stopped','failed','completed']){
 localStorage.setItem('moonbox.session',JSON.stringify({access_token:'synthetic'}));
 const partial=status!=='completed';
 global.fetch=async url=>{
  if(url.includes('/events'))return new Response('',{headers:{'Content-Type':'text/event-stream'}});
  const data=url.includes('/turns/')?{id:'t',status}:{items:[{id:'assistant-t',turn_id:'t',role:'assistant',content:'合成助手正文',created_at:'2026-10-08T10:00:00Z',output_partial:partial,output_truncated:partial,output_source:'events'}]};
  return new Response(JSON.stringify({code:0,data}));
 };
 render(React.createElement(ConversationMessages,{conversationId:'c',onTrace:()=>{}}));
 await screen.findByText('合成助手正文');
 if(partial)assert.match(screen.getByTestId('chat-partial-output').textContent,/不代表执行完成/);
 else assert.equal(screen.queryByTestId('chat-partial-output'),null);
 if(status==='unknown')await screen.findByText(/不要重复发送命令/);
 assert.equal(screen.getAllByText('合成助手正文').length,1);
 cleanup();
}
console.log('PASS: four DOM states; body readable once; partial and unknown semantics. Synthetic API; no browser layout claim.');
dom.window.close();
})().catch(e=>{console.error(e);process.exitCode=1;dom.window.close();});
