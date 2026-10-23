const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const ts = require('typescript');
const source = fs.readFileSync(path.join(__dirname, '../src/pages/catalog/governanceSession.ts'), 'utf8');
const compiled = ts.transpileModule(source, {compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}});
const exportsObject = {};
new Function('exports', compiled.outputText)(exportsObject);
const decide = exportsObject.governanceSessionDecision;
assert.deepEqual(decide({conversation_id:'original',view_conversation_id:'original',can_send:false,execution_state:'running'}),
  {conversationId:'original',replaceDraft:false,message:'对象正在执行，请查看当前执行'});
assert.equal(decide({conversation_id:'hidden',can_send:false}).conversationId,null);
assert.equal(decide({conversation_id:null,can_send:false,execution_state:'needs_review'}).replaceDraft,false);
assert.equal(decide({conversation_id:'original',can_send:true}).conversationId,'original');
assert.equal(decide({conversation_id:'original'}).replaceDraft,true);
assert.equal(decide({conversation_id:null}).replaceDraft,false);
console.log('6 synthetic governance session navigation assertions passed');
