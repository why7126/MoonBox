// Dependency-light fallback for environments missing Vitest's native Rollup binary.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const ts = require('typescript');
const source = fs.readFileSync(path.join(__dirname, '../src/pages/catalog/requirementOwner.ts'), 'utf8');
const compiled = ts.transpileModule(source, {compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2022}});
const exportsObject = {};
new Function('exports', compiled.outputText)(exportsObject);
const {normalizeOwner, ownerFilterOptions} = exportsObject;
for (const [owner, expected] of [['user_missing','未知用户'],['','未分配'],['null','未分配'],['product','产品团队'],['user','用户反馈'],['历史团队','历史团队']]) {
  assert.equal(normalizeOwner({owner}).owner, expected);
}
assert.deepEqual(normalizeOwner({owner:'user_a',owner_key:'user_a',owner_display_name:'昵称'}),{owner:'昵称',ownerKey:'user_a'});
assert.equal(normalizeOwner({owner:'user_a',owner_display_name:' '}).owner,'未知用户');
const issues=[{owner:'同名',owner_key:'user_b'},{owner:'同名',owner_key:'user_a'},{owner:'同名',owner_key:'user_b'}];
const options=ownerFilterOptions(issues);
assert.deepEqual(options,[{value:'user_a',label:'同名（1）'},{value:'user_b',label:'同名（2）'}]);
assert.deepEqual(ownerFilterOptions([...issues].reverse()),options);
assert.deepEqual(ownerFilterOptions([{owner:'user_a'},{owner:'user_b'}]).map(i=>i.label),['未知用户（1）','未知用户（2）']);
assert.equal(issues.map(normalizeOwner).filter(i=>i.ownerKey===options[0].value).length,1);
console.log('12 owner normalization/filter assertions passed (synthetic, no browser)');
