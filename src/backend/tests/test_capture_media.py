from io import BytesIO
from types import SimpleNamespace
import pytest
from app.chat.service import ChatError
from app.governance import capture_media, capture_drafts
from test_chat import chat
from test_governance_writer import writing


def png():
    from PIL import Image
    out=BytesIO();Image.new('RGB',(20,10),'white').save(out,format='PNG');return out.getvalue()


def test_decode_signature_and_static():
    from PIL import Image
    assert capture_media.decode(png(),'image/png')==(20,10)
    with pytest.raises(ChatError):capture_media.decode(png(),'image/jpeg')
    with pytest.raises(ChatError):capture_media.decode(b'\x89PNG\r\n\x1a\ninvalid','image/png')
    out=BytesIO();Image.new('RGB',(20,10),'red').save(out,format='PNG',save_all=True,append_images=[Image.new('RGB',(20,10),'blue')])
    with pytest.raises(ChatError):capture_media.decode(out.getvalue(),'image/png')


def test_private_upload_read_delete_and_quota(writing,monkeypatch):
    values={}
    class Storage:
        def put(self,key,content,mime):values[key]=SimpleNamespace(data=content,content_type=mime)
        def get(self,key):return values[key]
        def remove(self,key):values.pop(key,None)
    monkeypatch.setattr(capture_media,'get_object_storage',Storage)
    factory,project,*_=writing
    with factory() as db:
        draft=capture_drafts.create(db,'alice',project)
        result=capture_media.upload(db,'alice',project,draft['id'],png(),'image/png')
        assert 'object_key' not in result and result['width']==20
        assert capture_media.read(db,'alice',project,result['media_id']).data==png()
        with pytest.raises(ChatError):capture_media.read(db,'bob',project,result['media_id'])
        capture_drafts.remove(db,'alice',project,draft['id'],1)
        with pytest.raises(ChatError):capture_media.read(db,'alice',project,result['media_id'])


def test_deletion_ledger_replays_before_restored_draft_is_usable(writing,monkeypatch):
    from app.governance import capture_cleanup
    from app.governance.capture_schema import drafts,materials,revisions
    from sqlalchemy import update,select
    values={}
    class Storage:
        def put(self,key,content,mime):values[key]=content
        def get(self,key):return values[key]
        def remove(self,key):values.pop(key,None)
    monkeypatch.setattr(capture_media,'get_object_storage',Storage)
    factory,project,*_=writing
    with factory() as db:
        draft=capture_drafts.create(db,'alice',project)
        media=capture_media.upload(db,'alice',project,draft['id'],png(),'image/png')
        capture_drafts.remove(db,'alice',project,draft['id'],1)
        # Simulate loading an older DB that predates deletion; ledger is independent.
        db.execute(update(drafts).where(drafts.c.id==draft['id']).values(state='editing',deleted_at=None));db.commit()
        with pytest.raises(ChatError):capture_drafts.get(db,'alice',project,draft['id'])
        assert capture_cleanup.cleanup(db,Storage())==1 and not values
        assert db.scalar(select(drafts.c.state).where(drafts.c.id==draft['id']))=='deleted'
        assert not db.execute(select(revisions).where(revisions.c.draft_id==draft['id'])).all()
        assert capture_cleanup.cleanup(db,Storage())==0


def test_confirmed_images_leave_draft_quota_and_preserve_initial_source(writing,monkeypatch):
    from app.governance import capture_confirmations,readiness,capture_cleanup
    from app.governance.capture_schema import quotas,materials,confirmations
    from sqlalchemy import select,update
    import json
    values={}
    class Storage:
        def put(self,key,content,mime):values[key]=SimpleNamespace(data=content,content_type=mime)
        def get(self,key):return values[key]
        def remove(self,key):values.pop(key,None)
    monkeypatch.setattr(capture_media,'get_object_storage',Storage)
    factory,project,*_=writing;readiness.publish()
    with factory() as db:
        draft=capture_drafts.create(db,'alice',project)
        media=capture_media.upload(db,'alice',project,draft['id'],png(),'image/png')
        body={'text':'原始图文','media_ids':[media['media_id']], 'candidates':[{'type':'bug','severity':'medium',
            'title':'截图错误','description':'初次整理内容','source_refs':['text',media['media_id']]}]}
        saved=capture_drafts.save(db,'alice',project,draft['id'],1,body)
        item=saved['content']['candidates'][0];cid=item['id'];item.pop('severity');item.update(type='requirement',priority='P2',description='用户调整内容')
        capture_drafts.save(db,'alice',project,draft['id'],2,saved['content'])
        task=capture_confirmations.confirm(db,'alice',project,draft['id'],3,'once')
        frozen=json.loads(db.scalar(select(confirmations.c.payload).where(confirmations.c.id==task['id'])))
        assert frozen['origins'][cid]['candidate']['description']=='初次整理内容'
        assert frozen['candidates'][0]['type']=='requirement'
        assert db.scalar(select(quotas.c.material_bytes))==0
        assert db.scalar(select(materials.c.state))=='retained'
        db.execute(update(materials).values(created_at='2000-01-01T00:00:00+00:00'));db.commit()
        assert capture_cleanup.cleanup(db,Storage())==0
        assert capture_media.read(db,'alice',project,media['media_id']).data==png()


def test_interrupted_upload_keeps_cleanup_identity(writing,monkeypatch):
    from app.governance import capture_cleanup
    from app.governance.capture_schema import materials,quotas
    from sqlalchemy import update,select
    values={}
    class Storage:
        def put(self,key,content,mime):values[key]=content;raise SystemExit('power loss after PUT')
        def remove(self,key):values.pop(key,None)
    monkeypatch.setattr(capture_media,'get_object_storage',Storage)
    factory,project,*_=writing
    with factory() as db:
        draft=capture_drafts.create(db,'alice',project)
        with pytest.raises(SystemExit):capture_media.upload(db,'alice',project,draft['id'],png(),'image/png')
        db.rollback()
        assert db.scalar(select(materials.c.state))=='uploading'
        db.execute(update(materials).values(created_at='2000-01-01T00:00:00+00:00'));db.commit()
        assert capture_cleanup.cleanup(db,Storage())==1 and not values
        assert db.scalar(select(quotas.c.material_bytes))==0


def test_removed_uploads_release_slots_without_erasing_lineage(writing,monkeypatch):
    from app.governance.capture_schema import materials
    from sqlalchemy import select
    class Storage:
        def put(self,*args):pass
    monkeypatch.setattr(capture_media,'get_object_storage',Storage)
    factory,project,*_=writing
    with factory() as db:
        draft=capture_drafts.create(db,'alice',project)
        uploaded=[capture_media.upload(db,'alice',project,draft['id'],png(),'image/png') for _ in range(10)]
        with pytest.raises(ChatError):capture_media.upload(db,'alice',project,draft['id'],png(),'image/png')
        capture_drafts.save(db,'alice',project,draft['id'],1,{'text':'保留一张','media_ids':[uploaded[0]['media_id']],'candidates':[]})
        assert len(db.execute(select(materials).where(materials.c.state=='detached')).all())==9
        assert capture_media.upload(db,'alice',project,draft['id'],png(),'image/png')['state']=='ready'


def test_material_byte_quota_rejects_without_put(writing,monkeypatch):
    from app.governance.capture_schema import quotas,materials
    from sqlalchemy import update,select
    class Storage:
        def put(self,*args):raise AssertionError('quota rejection must precede storage')
    monkeypatch.setattr(capture_media,'get_object_storage',Storage)
    factory,project,*_=writing
    with factory() as db:
        draft=capture_drafts.create(db,'alice',project)
        db.execute(update(quotas).values(material_bytes=1024**3-len(png())+1));db.commit()
        with pytest.raises(ChatError):capture_media.upload(db,'alice',project,draft['id'],png(),'image/png')
        assert not db.execute(select(materials)).all()


def test_static_image_byte_and_pixel_boundaries():
    from PIL import Image
    content=png()
    assert capture_media.decode(content+b'\x00'*(10*1024*1024-len(content)),'image/png')==(20,10)
    with pytest.raises(ChatError):capture_media.decode(content+b'\x00'*(10*1024*1024-len(content)+1),'image/png')
    for width,accepted in [(5000,True),(5001,False)]:
        out=BytesIO();Image.new('RGB',(width,4000),'white').save(out,format='PNG')
        if accepted:assert capture_media.decode(out.getvalue(),'image/png')==(width,4000)
        else:
            with pytest.raises(ChatError):capture_media.decode(out.getvalue(),'image/png')
