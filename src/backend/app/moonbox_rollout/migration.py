"""Adopt only verified v2 content manifests; old summaries remain historical metadata."""
import hashlib
import json
from sqlalchemy import select
from app.chat import content_store, snapshot_store
from app.chat.content_schema import versions, objects
from app.moonbox_exec_server.scope import excluded
from . import catalog
from .schema import snapshot_points


def adopt(db, workspace, conversation_id):
    migrated = 0
    rows = db.execute(select(versions).where(versions.c.conversation_id == conversation_id,
        versions.c.status == 'complete').order_by(versions.c.created_at, versions.c.id)).mappings()
    for version in rows:
        if db.scalar(select(snapshot_points.c.point_id).where(snapshot_points.c.version_id == version['id'])):
            continue
        manifest = hashlib.sha256(); cursor = ''; complete = True
        while batch := snapshot_store.page(db, version['id'], cursor, 256):
            for item in batch:
                manifest.update(json.dumps([item[k] for k in ('path','kind','mode','digest','byte_count')],
                    ensure_ascii=False, separators=(',', ':')).encode())
                if excluded(item['path']) or item['kind'] != 'file' or not item['object_id']:
                    complete = False; continue
                obj = db.execute(select(objects).where(objects.c.id == item['object_id'],
                    objects.c.status == 'complete')).mappings().first()
                if not obj or (obj['sha256'],obj['byte_count']) != (item['digest'],item['byte_count']):
                    complete = False; continue
                digest = hashlib.sha256(); size = 0
                try:
                    for block in content_store.blocks(db, obj['id']):
                        digest.update(block); size += len(block)
                except ValueError:
                    complete = False; continue
                complete = complete and (digest.hexdigest(), size) == (item['digest'],item['byte_count'])
            cursor = batch[-1]['path_key']
        if not complete or manifest.hexdigest() != version['manifest_hash']:
            continue
        # The recorded HEAD is the migration anchor, not a claim about historical Git HEAD.
        # Unknown original scope deliberately disables whole-directory reconstruction.
        point = catalog.publish(db, workspace['id'], version['id'], policy_version='legacy-verified-v2',
            head_commit=workspace['base_commit'], changed=True, scope=None)
        catalog.reference(db, workspace['id'], point['id'], 'legacy_version', version['id'], 'legacy_verified')
        migrated += 1
    return migrated
