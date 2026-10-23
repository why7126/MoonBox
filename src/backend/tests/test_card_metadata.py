import math
from pathlib import Path
import pytest
import yaml
from app.governance.card_metadata import estimate_metadata, root_cause_metadata
from app.governance.change_index import ChangeIndex
from app.services.requirement_center import using_governance_root

ID = 'BUG-0100-tags'

@pytest.mark.parametrize('v,status', [(0,'available'),(.5,'available'),(3.25,'available'),(None,'invalid'),('', 'invalid'),('3','invalid'),(-1,'invalid'),(True,'invalid'),(math.inf,'invalid'),(math.nan,'invalid')])
def test_numbers(v,status):
    assert estimate_metadata([{'id':ID,'estimated_person_days':v}],ID,[])['estimate_status']==status


def test_total_partition_and_conflicts():
    rows=[{'id':ID,'bug':ID,'change':'one','estimated_person_days':3},{'id':'two','bug':ID,'change':'two','estimated_person_days':2}]
    assert estimate_metadata(rows,ID,['one','two'])['estimated_person_days']==3
    assert estimate_metadata(rows+[rows[0]],ID,['one','two'])['estimated_person_days']==3
    assert estimate_metadata(rows+[dict(rows[0],estimated_person_days=4)],ID,[])['estimate_status']=='conflict'
    parts=[{'id':c,'bug':ID,'change':c,'estimated_person_days':v} for c,v in [('one',.5),('two',1)]]
    assert estimate_metadata(parts,ID,['one','two'])['estimated_person_days']==1.5
    assert estimate_metadata(parts[:1],ID,['one','two'])['estimate_status']=='missing'

@pytest.mark.parametrize('key',['status','root_cause_status'])
@pytest.mark.parametrize('state',['unknown','hypothesis','probable','confirmed'])
def test_root_states(key,state):
    assert root_cause_metadata('## 根因分析\n请求缓存未失效。',{key:state})['root_cause_state']==('confirmed' if state=='confirmed' else 'pending')

@pytest.mark.parametrize('body',['','## 根因分析\n','## 根因分析\n待补充','## 根因分析\n- 直接原因：待填写','## 根因分析\n**分析结论：** TODO','## 根因状态\nstatus: confirmed','## 证据链\n| ID | 摘要 |\n| --- | --- |\n| E1 | 待填写 |'])
def test_empty(body):
    assert root_cause_metadata(body,{'status':'confirmed'})['root_cause_state']=='absent'


def test_root_conflicts_and_fallback():
    text='## 根因分析\n数据读取遗漏。\n## 根因状态\nstatus: confirmed'
    assert root_cause_metadata(text,{})['root_cause_state']=='confirmed'
    assert root_cause_metadata(text,{'status':'done','root_cause_status':'confirmed'})['root_cause_state']=='confirmed'
    assert root_cause_metadata(text,{'root_cause_status':'probable'})['root_cause_reason']=='conflict'
    assert root_cause_metadata(text,{'root_cause_status':[]})['root_cause_reason']=='invalid'


def write(p,text):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)


def test_real_projection_archived_and_visibility(tmp_path):
    folder=f'issues/bugs/archive/{ID}'
    write(tmp_path/'issues/requirements/_registry.yaml','entries: []\n')
    entry={'id':ID,'path':folder,'severity':'medium','iteration':'sprint-001','status':'done','title':'样本'}
    write(tmp_path/'issues/bugs/_registry.yaml',yaml.safe_dump({'entries':[entry]}))
    write(tmp_path/f'{folder}/trace.md','---\nstatus: done\niteration: sprint-001\n---\n')
    root=tmp_path/f'{folder}/root-cause.md'
    write(root,'---\nroot_cause_status: confirmed\n---\n## 根因分析\n缓存未及时失效。\n')
    write(tmp_path/'iterations/archive/sprint-001/sprint.yaml',yaml.safe_dump({'bugs':[ID],'scope_estimates':[{'id':ID,'estimated_person_days':0}]}))
    with using_governance_root(tmp_path,immutable=True):
        card=ChangeIndex(tmp_path).cards(lambda _:True)[0]
        assert card.root_cause_state=='confirmed' and card.estimated_person_days==0 and card.stage=='done'
        assert ChangeIndex(tmp_path).cards(lambda _:False)==[]
    write(root,root.read_text().replace('confirmed','hypothesis'))
    with using_governance_root(tmp_path,immutable=True):
        assert ChangeIndex(tmp_path).cards(lambda _:True)[0].root_cause_state=='pending'
    root.unlink()
    with using_governance_root(tmp_path,immutable=True):
        assert ChangeIndex(tmp_path).cards(lambda _:True)[0].root_cause_state=='absent'
