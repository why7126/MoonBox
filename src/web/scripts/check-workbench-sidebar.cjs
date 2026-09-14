// 仅合成 API 响应；对实际构建的两页进行共享侧边栏交互/样式验收。
const { chromium } = require('@playwright/test');
const fs = require('node:fs');
const assert = require('node:assert/strict');
const origin = process.argv[2] || 'http://localhost:18102';
const dir = '../../openspec/changes/add-chat-workbench-codex/evidence/sidebar-ui';
const workspace = { workspaceId:'s1', name:'隔离验收空间', organizationName:'视觉测试', slug:'synthetic', description:'', timezone:'UTC', memberCount:2, role:'拥有者' };
const readonly = {...workspace, workspaceId:'s2', name:'只读验收空间', readonly:true};
const context = { currentUser:{name:'验收用户',avatarInitial:'验收',avatarUrl:null,canAccessAdmin:true,permissions:[]}, workspaces:[workspace,readonly], selectedWorkspaceId:'s1', issues:[], stats:{total:0,requirements:0,bugs:0,blocked:0,drift:0} };
(async()=>{
 const browser = await chromium.launch({headless:true}); const samples=[]; const modalSamples=[]; const errors=[]; let screenshots=0;
 fs.mkdirSync(dir,{recursive:true});
 try {
  for(const [width,height] of [[1440,900],[1024,600],[390,844]]) for(const theme of ['dark','light']) {
   const pair={};
   for(const routeName of ['requirements','chat']) {
    const page=await browser.newPage({viewport:{width,height}});
    page.on('pageerror', e=>errors.push(e.message));
    await page.addInitScript(({theme})=>{localStorage.setItem('moonbox.session',JSON.stringify({username:'验收用户',access_token:'synthetic-test-token'}));if(!localStorage.getItem('moonbox.ui.preferences'))localStorage.setItem('moonbox.ui.preferences',JSON.stringify({theme}));},{theme});
    await page.route('**/api/**',async route=>{
     const req=route.request(),url=new URL(req.url()); assert.equal(req.method(),'GET','视觉检查不得写入后端');
     let data;
     if(url.pathname==='/api/v1/requirement-center/context') data=context;
     else if(url.pathname.endsWith('/spaces')) data=[{id:'s1',name:workspace.name},{id:'s2',name:readonly.name}];
     else if(url.pathname.endsWith('/capabilities')) data={execution_ready:false,reason:'隔离视觉验收：真实执行未开启',repositories:[]};
     else data={items:[],total:0,page:1,page_size:20};
     await route.fulfill({json:{code:0,data,message:'成功'}});
    });
    await page.goto(origin+'/'+routeName); await page.locator('.rc-user-trigger').filter({hasText:'验收'}).waitFor();
    await page.evaluate(()=>document.fonts.ready);
    assert.equal(await page.locator('.requirement-center').getAttribute('data-theme'),theme);
    pair[routeName]={};
    for(const collapsed of [false,true]) {
     if((await page.locator('.rc-sidebar').getAttribute('class')).includes('collapsed')!==collapsed) await page.locator('.rc-collapse').click();
     await page.waitForTimeout(250);
     const state=collapsed?'collapsed':'expanded';
     const styles=await page.evaluate(()=>{
      const result={};
      for(const selector of ['.rc-sidebar','.rc-brand','.rc-nav-group-label','.rc-nav-item:not(.active)','.rc-nav-item.active','.rc-nav-icon','.rc-user-trigger']){
       const el=document.querySelector(selector),s=getComputedStyle(el),r=el.getBoundingClientRect();
       result[selector]={width:r.width,height:r.height,padding:s.padding,gap:s.gap,fontSize:s.fontSize,lineHeight:s.lineHeight,color:s.color,background:s.backgroundColor,border:s.border,borderRadius:s.borderRadius,display:s.display,overflow:s.overflow};
      }
      return result;
     });
     pair[routeName][state]=styles; samples.push({page:routeName,theme,width,height,state,styles});
     screenshots++; await page.screenshot({path:`${dir}/${routeName}-${theme}-${width}-${state}.png`});
     const footer=await page.locator('.rc-user-trigger').boundingBox(); assert(footer&&footer.y>=0&&footer.y+footer.height<=height+1,'用户菜单可达');
    }
    if (theme==='light' && (width===1440 || width===390)) {
     for(const [name,selector,entry] of [
      ['profile','.rc-profile-modal','个人资料'], ['password','.admin-password-modal','修改密码'],
      ['settings','.rc-space-settings','设置空间'], ['create','.rc-space-application','创建空间']
     ]) {
      await page.locator('.rc-user-trigger').click();
      if(name==='create') {await page.getByRole('menuitem',{name:'切换空间'}).click();await page.getByTestId('space-create-or-join-entry').click();}
      else await page.getByRole('menuitem',{name:entry}).click();
      const modal = name==='password' ? page.getByRole('form',{name:'修改密码'}) : page.locator(selector);
      await modal.waitFor();
      const box=await modal.boundingBox(); assert(box&&box.x>=-1&&box.x+box.width<=width+1,`${name} 弹窗横向可达`);
      modalSamples.push({page:routeName,width,height,name,style:await modal.evaluate(e=>{const s=getComputedStyle(e),r=e.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height,padding:s.padding,background:s.backgroundColor,overflow:s.overflow,borderRadius:s.borderRadius,scrollHeight:e.scrollHeight,clientHeight:e.clientHeight};})});
      const cancel = modal.getByRole('button',{name:'取消',exact:true});
      if(await cancel.count()){await cancel.scrollIntoViewIfNeeded();const r=await cancel.boundingBox();assert(r&&r.y>=0&&r.y+r.height<=height+1,`${name} 取消操作可达`);}
      screenshots++; await page.screenshot({path:`${dir}/${routeName}-light-${width}-${name}.png`});
      await page.keyboard.press('Escape');
     }
    }
    // 折叠后的菜单、触控空间切换、只读权限以及 Esc 焦点返回。
    await page.locator('.rc-user-trigger').click();
    await page.getByRole('menuitem',{name:'进入后台'}).waitFor();
    screenshots++; await page.screenshot({path:`${dir}/${routeName}-${theme}-${width}-menu.png`});
    await page.getByRole('menuitem',{name:'切换空间'}).click();
    const pop=await page.getByTestId('space-switcher-popover').boundingBox(); assert(pop&&pop.x>=0&&pop.x+pop.width<=width+1,'空间浮层在视口内');
    await page.getByTestId('space-option-s2').click();
    await page.locator('.rc-user-trigger').click(); assert.equal(await page.getByRole('menuitem',{name:'设置空间'}).count(),0);
    await page.keyboard.press('Escape'); assert.equal(await page.getByRole('menu').count(),0);
    assert(await page.locator('.rc-user-trigger').evaluate(e=>e===document.activeElement));
    // 两页主题持久化；跨路由后状态仍一致。
    await page.locator('.rc-user-trigger').click(); await page.getByRole('switch',{name:'切换明暗主题'}).click();
    const nextTheme=theme==='light'?'dark':'light'; assert.equal(await page.locator('.requirement-center').getAttribute('data-theme'),nextTheme);
    await page.keyboard.press('Escape');
    await page.getByRole('navigation').getByRole('button',{name:routeName==='chat'?'需求中心':'Chat 工作台'}).click();
    await page.waitForURL('**/'+(routeName==='chat'?'requirements':'chat'));
    await page.locator('.rc-sidebar').waitFor(); assert.equal(await page.locator('.requirement-center').getAttribute('data-theme'),nextTheme);
    await page.close();
   }
   assert.deepEqual(pair.chat,pair.requirements,`两页 computed style 应相同：${theme} ${width}`);
  }
  assert.deepEqual(errors,[]);
  fs.writeFileSync(`${dir}/computed.json`,JSON.stringify({boundary:'synthetic API; no model execution; no server mutations',samples,modalSamples,errors},null,2));
  console.log(JSON.stringify({status:'pass',screenshots,comparisons:12,viewports:3,themes:2,errors:0}));
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
