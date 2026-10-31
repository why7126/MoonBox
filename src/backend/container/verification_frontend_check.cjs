'use strict';
// Deployment-approved entry. Candidate files are read-only; caches stay in tmpfs.
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {spawnSync} = require('node:child_process');
const project = '/source/src/web';
const artifact = '/app/src/web';
const checks = process.argv.slice(2);
if (!checks.length || checks.some(p => !/^src\/[a-zA-Z0-9_./-]+\.(test|spec)\.[jt]sx?$/.test(p) || p.split('/').includes('..'))) process.exit(2);
if (!fs.readFileSync(path.join(project,'pnpm-lock.yaml')).equals(fs.readFileSync(path.join(artifact,'pnpm-lock.yaml')))) process.exit(3);
const work = fs.mkdtempSync(path.join(os.tmpdir(),'moonbox-component-'));
try {
 for (const file of ['src','package.json','pnpm-lock.yaml','vitest.config.ts','tsconfig.json']) {
  const source=path.join(project,file);
  fs.cpSync(source,path.join(work,file),{recursive:true,dereference:false});
 }
 fs.symlinkSync(path.join(artifact,'node_modules'),path.join(work,'node_modules'));
 const result=spawnSync(process.execPath,[path.join(artifact,'node_modules/vitest/vitest.mjs'),'run','--no-cache',...checks],{cwd:work,stdio:'inherit',timeout:120000});
 process.exitCode=result.status===0?0:1;
} finally {fs.rmSync(work,{recursive:true,force:true});}
