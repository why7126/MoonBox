"""真实浏览器验收，参数为 capture_live_harness 的私有临时目录。"""
import json, sys
from pathlib import Path
import yaml
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3]
root=Path(sys.argv[1]);cfg=json.loads((root/'browser.json').read_text())
evidence=ROOT/'openspec/changes/fix-requirement-center-capture-persistence/evidence';evidence.mkdir(exist_ok=True)
report={'source':'observed','viewport_checks':[],'objects':[],'requests':[]}
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    page=browser.new_page(has_touch=True, viewport={'width':1440,'height':1000})
    response=page.request.post(cfg['url']+'/api/v1/auth/login',data={'username':'alice','password':cfg['password'],'remember_me':False})
    assert response.ok
    session=response.json()['data'];session['username']='alice'
    page.add_init_script('localStorage.setItem("moonbox.session", '+json.dumps(json.dumps(session))+')')
    def received(response):
        if '/captures?' in response.url or '/governance-applications/' in response.url:
            data=response.json().get('data') or {}
            report['requests'].append({'status':response.status,'operation_id':data.get('id'),'state':data.get('state'),'object_id':data.get('object_id'),'request_id':response.headers.get('x-request-id')})
    page.on('response',received)
    page.goto(cfg['url']+'/requirements');page.wait_for_load_state('networkidle')
    for kind,prefix,width in [('requirement','REQ',1440),('bug','BUG',390)]:
        page.set_viewport_size({'width':width,'height':1000 if width==1440 else 844})
        page.get_by_role('button',name='新建 Capture',exact=True).click()
        title=page.get_by_label('Capture 标题',exact=True)
        title.wait_for();page.locator('.rc-capture-readiness').wait_for(state='hidden');assert title.evaluate('(e)=>e===document.activeElement')
        dialog=page.get_by_role('dialog',name='新建 Capture',exact=True)
        dialog.locator('[data-type="'+kind+'"]').click()
        grading=dialog.get_by_role('group',name='Capture 严重性' if kind=='bug' else 'Capture 优先级',exact=True)
        assert grading.get_by_role('button').count()==(5 if kind=='bug' else 4)
        if kind=='bug':
            grading.get_by_role('button',name='严重',exact=True).click()
            page.set_viewport_size({'width':1440,'height':1000})
            page.screenshot(path=str(evidence/'quiet-bug-1440.png'))
            page.set_viewport_size({'width':390,'height':844})
        if kind=='requirement': grading.get_by_role('button',name='P3',exact=True).click()
        report.setdefault('grading',[]).append(grading.evaluate("e=>({label:e.getAttribute('aria-label'),width:e.getBoundingClientRect().width,buttons:[...e.querySelectorAll('button')].map(b=>({text:b.textContent,selected:b.getAttribute('aria-pressed'),width:b.getBoundingClientRect().width,scrollWidth:b.scrollWidth,clientWidth:b.clientWidth,color:getComputedStyle(b).color,background:getComputedStyle(b).backgroundColor}))})"))
        chosen=grading.get_by_role('button',name='严重' if kind=='bug' else 'P3',exact=True)
        chosen.hover()
        assert dialog.get_by_role('tooltip').count()==0
        chosen.focus()
        assert dialog.get_by_role('tooltip').count()==0
        assert dialog.locator('.rc-capture-readiness').count()==0
        assert dialog.locator('.rc-level-description').count()==1
        report['no_tooltip_or_ready_container']=True
        chosen.press('Enter')
        assert chosen.get_attribute('aria-pressed')=='true'
        page.screenshot(path=str(evidence/f'quiet-focus-{width}.png'))
        if kind=='bug':
            chosen.tap();assert chosen.get_attribute('aria-pressed')=='true'
            report['touch_description']=dialog.locator('.rc-level-description').inner_text()
            assert '核心功能严重受损' in report['touch_description']
        assert dialog.locator('.rc-level-description').inner_text()
        if kind=='requirement': assert round(dialog.bounding_box()['width'])==840
        if kind=='requirement':
            page.set_viewport_size({'width':390,'height':844})
            assert grading.evaluate('(e)=>e.scrollWidth<=e.clientWidth')
            page.screenshot(path=str(evidence/'quiet-req-390.png'))
            page.set_viewport_size({'width':1440,'height':1000})
        title.fill(prefix+' 浏览器持久化验收')
        page.get_by_label('一句话描述',exact=True).fill('真实描述完整保留，重载后读取文件。')
        button=dialog.get_by_role('button',name='＋ 创建 Capture',exact=True)
        button.scroll_into_view_if_needed()
        report['viewport_checks'].append(dialog.evaluate('''e=>({width:innerWidth,dialogWidth:e.getBoundingClientRect().width,maxHeight:getComputedStyle(e).maxHeight,overflowY:getComputedStyle(e).overflowY,buttonBottom:e.querySelector('[type=submit]').getBoundingClientRect().bottom,viewportHeight:innerHeight})'''))
        page.screenshot(path=str(evidence/f'quiet-capture-{width}.png'))
        if kind=='bug':
            permit=root/'private/maintenance.json';original=permit.read_bytes();permit.unlink()
            button.click();page.get_by_role('alert').wait_for(timeout=10000)
            assert title.input_value()==prefix+' 浏览器持久化验收'
            button.scroll_into_view_if_needed();button.focus()
            assert button.evaluate('(e)=>e===document.activeElement && e.getBoundingClientRect().bottom<=innerHeight')
            page.screenshot(path=str(evidence/'capture-error-390.png'))
            permit.write_bytes(original);permit.chmod(0o600)
        button.click();page.get_by_text('Capture 已创建并插入采集池',exact=True).wait_for(timeout=20000)
        page.reload();page.wait_for_load_state('networkidle')
        folder='requirements' if kind=='requirement' else 'bugs'
        registry=yaml.safe_load((root/'project/issues'/folder/'_registry.yaml').read_text())
        entry=next(e for e in registry['entries'] if e['title']==prefix+' 浏览器持久化验收')
        assert entry['severity' if kind=='bug' else 'priority']==('critical' if kind=='bug' else 'P3')
        assert ('priority' if kind=='bug' else 'severity') not in entry
        short='-'.join(entry['id'].split('-')[:2])
        card=page.locator('[data-issue-id="'+short+'"]');card.wait_for()
        card.get_by_role('button',name='capture.md',exact=True).click()
        page.get_by_text('真实描述完整保留，重载后读取文件。',exact=False).first.wait_for()
        page.screenshot(path=str(evidence/f'document-{prefix.lower()}.png'))
        files=[entry['path']+'capture.md',entry['path']+'trace.md',f'issues/{folder}/_registry.yaml',f'issues/{folder}/CHANGELOG.md']
        assert all((root/'project'/f).is_file() for f in files)
        report['objects'].append({'id':entry['id'],'files':files,'reload_and_document':True})
        page.goto(cfg['url']+'/requirements');page.wait_for_load_state('networkidle')
    browser.close()
(evidence/'quiet-browser-observed.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
