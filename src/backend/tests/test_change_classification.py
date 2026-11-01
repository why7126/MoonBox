import pytest
from app.governance.change_classification import classification, validate_assessment
from app.governance.change_priority import plan
from app.governance.reader import version
from app.chat.service import ChatError
from test_change_visibility import change, cards
from test_governance_scope import fixture_tree

@pytest.mark.parametrize('cid,meta,dimension,state,value', [
    ('fix-sample', {'priority':'P1'}, 'severity','missing',''),
    ('fix-sample', {'severity':'high'}, 'severity','valid','high'),
    ('update-sample', {'priority':'P2'}, 'priority','valid','P2'),
    ('fix-sample', {'change_type':'non_fix','priority':'P1'}, 'priority','invalid',''),
    ('update-sample', {'change_type':[], 'priority':'P1'}, 'priority','invalid',''),
    ('fix-sample', {'severity':'P1'}, 'severity','invalid',''),
    ('fix-sample', {'severity':'high','classification':{'state':'pending','dimension':'severity'}}, 'severity','missing',''),
])
def test_projection(cid,meta,dimension,state,value):
    result=classification(cid,meta)
    assert result['classification_dimension']==dimension
    assert result['classification_state']==state
    assert result[dimension]==value

def test_creation_requires_evidence_and_preserves_input():
    data={'change_type':'fix','severity':'high','classification':{'state':'assessed','dimension':'severity','rationale':'核心流程阻断但有替代方案','evidence_refs':['proposal.md'],'evaluated_at':'2026-11-01 01:00:00','evaluated_by':'agent'}}
    assert validate_assessment('fix-sample',data)['severity']=='high'
    data['classification']['evidence_refs']=[]
    with pytest.raises(ValueError): validate_assessment('fix-sample',data)
    data['classification']['state']='pending'
    with pytest.raises(ValueError): validate_assessment('fix-sample',data)

def test_card_and_old_writer_type_guard(tmp_path):
    root=fixture_tree(tmp_path)
    folder=change(root,'fix-sample',severity='high',priority='P1')
    row=next(r for r in cards(root).issues if r.id=='fix-sample')
    assert row.severity=='high' and row.priority=='' and not row.can_edit_priority
    before=(folder/'trace.md').read_text()
    with pytest.raises(ChatError): plan(root,'fix-sample','P2',version(before),'actor','2026-11-01 01:00:00')
    assert (folder/'trace.md').read_text()==before

def test_cli_initializer_reads_nested_assessment(tmp_path):
    import sys, yaml
    from pathlib import Path
    from types import SimpleNamespace
    sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'scripts'))
    from workflow_sync.initialization import initialize
    folder=tmp_path.resolve()/'openspec/changes/fix-sample';folder.mkdir(parents=True)
    data={'status':'proposed','change_type':'fix','severity':'high','classification':{'state':'assessed','dimension':'severity','rationale':'关键路径受影响','evidence_refs':['proposal.md'],'evaluated_at':'2026-11-01 00:40:00','evaluated_by':'agent'}}
    path=folder/'trace.md';path.write_text('---\n'+yaml.safe_dump(data,allow_unicode=True)+'---\n')
    record=SimpleNamespace(change_id='fix-sample',location='active',tasks=SimpleNamespace(done=0))
    before=path.read_bytes();result=initialize(tmp_path.resolve(),record,write=True)
    assert validate_assessment('fix-sample',result)['severity']=='high'
    assert path.read_bytes()==before
