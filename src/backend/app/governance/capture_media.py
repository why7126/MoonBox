"""Private images with server-side decode limits and transactional quota reservations."""
from io import BytesIO
from uuid import uuid4
import warnings
from sqlalchemy import insert, select, update
from app.chat.service import identity, now, ChatError
from app.core.object_storage import get_object_storage, ObjectStorageError
from app.governance import capture_drafts as drafts
from app.governance.capture_schema import drafts as draft_table, materials, quotas


def decode(content, mime):
    from PIL import Image, UnidentifiedImageError
    if mime not in drafts.LIMITS['image_types'] or not content or len(content)>drafts.LIMITS['max_image_bytes']:
        drafts.error('仅支持10 MiB以内的静态 PNG/JPEG/WebP 图片',422)
    signatures={'image/png':b'\x89PNG\r\n\x1a\n','image/jpeg':b'\xff\xd8\xff','image/webp':b'RIFF'}
    if not content.startswith(signatures[mime]):drafts.error('图片签名与格式不符',422)
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error',Image.DecompressionBombWarning)
            with Image.open(BytesIO(content)) as image:
                expected={'image/png':'PNG','image/jpeg':'JPEG','image/webp':'WEBP'}[mime]
                if image.format!=expected or getattr(image,'n_frames',1)!=1 or image.width*image.height>20_000_000:
                    drafts.error('图片格式、动画或像素数量不受支持',422)
                size=image.size;image.verify()
            with Image.open(BytesIO(content)) as image:image.load()
        return size
    except (OSError,ValueError,SyntaxError,UnidentifiedImageError,Image.DecompressionBombError,Image.DecompressionBombWarning):
        drafts.error('图片无法安全解码',422)


def upload(db, actor, project, draft_id, content, mime):
    draft=drafts.get(db,actor,project,draft_id,write=True)
    if draft['state']!='editing':drafts.error('已确认草稿不能追加图片')
    width,height=decode(content,mime)
    # Acquire the same row lock/CAS boundary as delete/confirm for both SQLite and MySQL.
    held=db.execute(update(draft_table).where(draft_table.c.id==draft_id,draft_table.c.state=='editing',
        draft_table.c.revision==draft['revision']).values(updated_at=now()))
    if held.rowcount!=1:db.rollback();drafts.error()
    rows=db.execute(select(materials).where(materials.c.draft_id==draft_id,materials.c.state.in_(('ready','uploading')))).mappings().all()
    if len(rows)>=10 or sum(row['size'] for row in rows)+len(content)>50*1024*1024:
        db.rollback();drafts.error('当前草稿图片数量或总量超限',422,reason='quota_exceeded')
    reserved=db.execute(update(quotas).where(quotas.c.actor_id==actor,quotas.c.scope_key==project.key,
        quotas.c.material_bytes+len(content)<=1024**3).values(material_bytes=quotas.c.material_bytes+len(content)))
    if reserved.rowcount!=1:db.rollback();drafts.error('草稿材料已达1 GiB，请先清理',422,reason='quota_exceeded')
    row={**identity(),'draft_id':draft_id,'actor_id':actor,'scope_key':project.key,
         'object_key':f'images/original/{uuid4()}.{dict(zip(drafts.LIMITS["image_types"],["png","jpg","webp"]))[mime]}',
         'mime_type':mime,'size':len(content),'width':width,'height':height,'state':'uploading','deleted_at':None}
    # Persist the opaque object identity before PUT so a process crash cannot orphan it.
    db.execute(insert(materials).values(**row));db.commit()
    try:
        current=drafts.get(db,actor,project,draft_id,write=True)
        held=db.execute(update(draft_table).where(draft_table.c.id==draft_id,draft_table.c.state=='editing',
            draft_table.c.revision==current['revision']).values(updated_at=now()))
        if held.rowcount!=1:raise ValueError('draft_changed')
        get_object_storage().put(row['object_key'],content,mime)
        db.execute(update(materials).where(materials.c.id==row['id'],materials.c.state=='uploading')
            .values(state='ready',updated_at=now()));db.commit();row['state']='ready'
    except Exception:
        db.rollback()
        db.execute(update(materials).where(materials.c.id==row['id'],materials.c.state=='uploading')
            .values(state='delete_pending',updated_at=now()));db.commit()
        raise ChatError(2605,'图片保存失败，请重试',503,kind='material_unreadable') from None
    return public(row)


def public(row):
    return {'media_id':row['id'],'mime_type':row['mime_type'],'size':row['size'],
            'width':row['width'],'height':row['height'],'state':row['state'],
            'preview_url':f'/api/v1/requirement-center/capture-materials/{row["id"]}/content'}


def read(db,actor,project,media_id):
    drafts.authorize(db,actor,project)
    row=db.execute(select(materials).where(materials.c.id==media_id,materials.c.actor_id==actor,
        materials.c.scope_key==project.key,materials.c.state.in_(('ready','retained','detached')),materials.c.deleted_at.is_(None))).mappings().first()
    if not row:raise ChatError(2601,'图片不存在或无权访问',404)
    drafts.get(db,actor,project,row['draft_id'])
    try:return get_object_storage().get(row['object_key'])
    except (ObjectStorageError,FileNotFoundError):raise ChatError(2605,'图片暂不可读，请重试',503,kind='material_unreadable') from None
