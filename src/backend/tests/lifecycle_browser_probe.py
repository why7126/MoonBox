"""Observed lifecycle acceptance; uses real login/API, CLI writes and browser polling."""
import json, sys, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
root=Path(sys.argv[1]);cfg=json.loads((root/'browser.json').read_text())
project=Path(__file__).resolve().parents[3]
evidence=project/'openspec/changes/fix-requirement-center-apply-lifecycle-sync/evidence';evidence.mkdir(exist_ok=True)
report={'source':'observed','network_mocked':False,'synthetic_accounts_and_project':True,'contexts':[],'cli':[],'checks':[]}
with sync_playwright() as p:
    browser=p.chromium.launch(headless=True)
    page=browser.new_page(viewport={'width':1440,'height':1000})
    login=page.request.post(cfg['url']+'/api/v1/auth/login',data={'username':'alice','password':cfg['password'],'remember_me':False});assert login.ok
    session=login.json()['data'];session['username']='alice'
    page.add_init_script('localStorage.setItem("moonbox.session", '+json.dumps(json.dumps(session))+')')
    def received(response):
        if '/requirement-center/context?' in response.url and response.status==200:
            data=response.json()['data'];report['contexts'].append({'revision':data['snapshot_revision'],'status':response.status,'issues':[{'id':i['id'],'stage':i['stage'],'tasks':i.get('tasks'),'action':i.get('action',{}).get('label')} for i in data['issues']]})
    page.on('response',received)
    page.goto(cfg['url']+'/requirements');page.wait_for_load_state('networkidle')
    cards=page.locator('[data-issue-id]');cards.first.wait_for(timeout=15000)
    assert cards.count()==2
    page.screenshot(path=str(evidence/'before-start-1440.png'),full_page=True)
    print(json.dumps({'recon':cards.evaluate_all('(els)=>els.map(e=>({id:e.dataset.issueId,stage:e.closest("[data-stage]").dataset.stage,text:e.innerText}))')},ensure_ascii=False),flush=True)
    for kind,prefix in [('requirement','REQ'),('bug','BUG')]:
        card=page.locator('[data-issue-id="'+prefix+'-9091"]')
        assert card.evaluate('(e)=>e.closest("[data-stage]").dataset.stage')=='ready-dev'
        change='fix-'+kind+'-lifecycle'
        def cli(event, expected=0):
            result=subprocess.run([sys.executable,str(root/'project/scripts/sync-workflow-status.py'),'--event',event,'--change',change,'--sprint','auto'],cwd=root/'project',capture_output=True,text=True)
            report['cli'].append({'event':event,'change':change,'exit_code':result.returncode})
            assert result.returncode==expected, result.stdout+result.stderr
        cli('opsx.start')
        # Wait for the existing polling loop, without forcing a frontend state change.
        page.wait_for_function('(id)=>document.querySelector(`[data-issue-id="${id}"]`)?.closest("[data-stage]").dataset.stage==="development"',arg=prefix+'-9091',timeout=15000)
        assert '0/2' in card.inner_text();assert '查看进度' in card.inner_text()
        card.scroll_into_view_if_needed();page.screenshot(path=str(evidence/(kind+'-started-1440.png')),full_page=True)
        report['checks'].append({'kind':kind,'stage':'development','done':0,'polling':True,'card_style':card.evaluate('(e)=>({fontSize:getComputedStyle(e).fontSize,display:getComputedStyle(e).display,width:e.getBoundingClientRect().width})')})
        cli('opsx.start');cli('opsx.progress')
        page.get_by_role('button',name='刷新需求中心',exact=True).click()
        expect(card).to_contain_text('0/2')
        page.reload();page.wait_for_load_state('networkidle');expect(card).to_contain_text('查看进度')
        tasks=root/'project/openspec/changes'/change/'tasks.md';tasks.write_text(tasks.read_text().replace('[ ]','[x]'))
        cli('opsx.progress')
        page.get_by_role('button',name='刷新需求中心',exact=True).click();expect(card).to_contain_text('2/2')
        assert card.evaluate('(e)=>e.closest("[data-stage]").dataset.stage')=='development'
        cli('opsx.apply');page.bring_to_front();page.evaluate('window.dispatchEvent(new Event("focus"))')
        page.wait_for_function('(id)=>document.querySelector(`[data-issue-id="${id}"]`)?.closest("[data-stage]").dataset.stage==="acceptance"',arg=prefix+'-9091')
        report['checks'].append({'kind':kind,'completion':'acceptance','manual_refresh':True,'reload':True,'focus_refresh':True})
    page.screenshot(path=str(evidence/'completed-1440.png'),full_page=True)
    browser.close()
assert len({c['revision'] for c in report['contexts']})>=5
(evidence/'browser-lifecycle.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'result':'passed','checks':len(report['checks']),'cli_events':len(report['cli']),'distinct_snapshots':len({c['revision'] for c in report['contexts']})}))
