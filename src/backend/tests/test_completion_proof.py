import pytest
import yaml
from app.governance.completion_proof import verify, ProofError
from app.governance.snapshot import digest


def fixture():
    oid='REQ-9001-proof'; base=f'issues/requirements/review/{oid}'
    def doc(**fields):
        return ('---\n'+yaml.safe_dump(fields)+'---\n# 样本\n').encode()
    files={'issues/requirements/_registry.yaml':yaml.safe_dump({'entries':[dict(id=oid,path=base,status='approved')]}).encode(),
           f'{base}/trace.md':doc(status='approved'), f'{base}/requirement.md':doc(status='approved',title='样本'),
           f'{base}/review.md':b'# approved', 'rules/global.md':b'# rules'}
    baseline={'workspace_mode':'source','files':{k:v.decode() for k,v in files.items()}}
    result={'after':{}}
    proof={'object_id':oid,'event':'req.review','source_hash':digest(files)}
    return oid, files, baseline, result, proof


def test_unrelated_docs_and_other_registry_entries_do_not_invalidate_completion():
    oid,files,b,r,p=fixture(); current=dict(files);current['docs/unrelated.md']=b'new'
    reg=yaml.safe_load(current['issues/requirements/_registry.yaml']);reg['entries'].append({'id':'REQ-9999-other','status':'draft'})
    current['issues/requirements/_registry.yaml']=yaml.safe_dump(reg).encode()
    assert verify(b,r,p,current,oid,'req-review')


@pytest.mark.parametrize('mutation',['result','rules','proof','identity'])
def test_relevant_change_or_tampering_rejected(mutation):
    oid,files,b,r,p=fixture();current=dict(files)
    if mutation=='result': current[f'issues/requirements/review/{oid}/review.md']=b'changed'
    if mutation=='rules': current['rules/global.md']=b'changed'
    if mutation=='proof': p['source_hash']='tampered'
    if mutation=='identity': p['object_id']='REQ-9999-other'
    with pytest.raises(ProofError): verify(b,r,p,current,oid,'req-review')


def test_deleted_dependency_recreated_is_conflict():
    oid, files, b, r, p = fixture()
    r['after']['docs/written-and-deleted.md'] = None
    current = dict(files); current['docs/written-and-deleted.md'] = b'recreated'
    with pytest.raises(ProofError, match='dependency_conflict'):
        verify(b, r, p, current, oid, 'req-review')


def test_handoff_schema_is_portable_and_additive():
    from sqlalchemy import create_engine
    from sqlalchemy.schema import CreateTable
    from sqlalchemy.dialects import mysql
    from app.governance.completion_handoff import handoffs
    engine = create_engine('sqlite://')
    handoffs.create(engine, checkfirst=True)
    handoffs.create(engine, checkfirst=True)
    assert 'PRIMARY KEY' in str(CreateTable(handoffs).compile(dialect=mysql.dialect()))
    engine.dispose()


@pytest.mark.parametrize('part',['baseline','result','proof'])
def test_malformed_private_record_is_rejected(part):
    oid,files,b,r,p=fixture()
    if part=='baseline': b=[]
    if part=='result': r=[]
    if part=='proof': p=[]
    with pytest.raises(ProofError,match='proof_invalid'):
        verify(b,r,p,files,oid,'req-review')
