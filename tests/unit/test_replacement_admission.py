"""Admission returns stable safe metadata without publishing candidate history."""
from sqlalchemy import select,update
from test_replacement_coordinator import orchestration
from app.governance import replacement_admission as admission,replacement_coordinator
from app.governance.replacement_schema import proposals,commits


def test_admission_readonly_and_version_bound(orchestration,monkeypatch):
    c=orchestration
    for name in ('load','validate','authorize_write','change_acceptance'):
        monkeypatch.setattr(admission,name,getattr(replacement_coordinator,name))
    row=c.db.execute(select(proposals)).mappings().one()
    result=admission.admit(c.db,c.project,'owner',row)
    assert result['decision']=='ready' and result['proposal_revision']==2
    assert len(result['input_fingerprint'])==64
    assert not c.proof.exists() and not c.db.execute(select(commits)).first()
    c.db.execute(update(proposals).values(state='revoked',revision=3));c.db.commit()
    result=admission.admit(c.db,c.project,'owner',c.db.execute(select(proposals)).mappings().one())
    assert result['decision']=='blocked' and result['reason_code']=='authorization_required'


def test_independent_gate_remains_separate(orchestration,monkeypatch):
    c=orchestration
    for name in ('load','validate','authorize_write'):
        monkeypatch.setattr(admission,name,getattr(replacement_coordinator,name))
    monkeypatch.setattr(admission,'change_acceptance',lambda *args,**kwargs:{'ready':False,'reason':'private/path must not leak'})
    result=admission.admit(c.db,c.project,'owner',c.db.execute(select(proposals)).mappings().one())
    assert result['blockers']==['independent_archive_gate_blocked']
    assert 'private/path' not in str(result) and not c.proof.exists()
