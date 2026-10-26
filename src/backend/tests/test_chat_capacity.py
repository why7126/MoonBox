"""Opt-in synthetic capacity samples; never substitutes for real model evidence."""
import hashlib
import json
import os
import resource
import time
import pytest
from test_chat import chat, create, queued
from app.chat import content_store, snapshot_store
from app.chat.content_schema import entries
from sqlalchemy import select, func

pytestmark = pytest.mark.skipif(os.environ.get('CHAT_CAPACITY_TEST') != '1', reason='explicit isolated capacity run required')


def test_capacity_snapshot(chat, tmp_path):
    client, factory = chat; cid = create(client); tid = queued(factory, cid)
    count = int(os.environ.get('CHAT_CAPACITY_FILES', '12000'))
    root = tmp_path / 'capacity'; root.mkdir()
    # 12,000 x 52,429 is just above 600 MiB, with distinct contents per file.
    size = 52429
    for index in range(count):
        prefix = f'{index:016d}'.encode()
        (root / f'f{index:06d}.txt').write_bytes(prefix + b'x' * (size-len(prefix)))
    started = time.monotonic()
    version = snapshot_store.capture(factory, cid, tid, root, 'before')
    elapsed = time.monotonic()-started
    with factory() as db:
        actual_count = db.scalar(select(func.count()).select_from(entries).where(entries.c.version_id == version['version_id']))
        total = db.scalar(select(func.sum(entries.c.byte_count)).where(entries.c.version_id == version['version_id']))
    assert actual_count == count and total == count*size
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if __import__('sys').platform != 'darwin': peak *= 1024
    print('CAPACITY_SNAPSHOT', json.dumps({'files':count,'bytes':total,'seconds':round(elapsed,3),'peak_rss_bytes':peak,'synthetic':True}))
    assert peak <= 512*1024*1024
    if count == 12000: assert elapsed <= 180


def test_capacity_result(chat):
    client, factory = chat; cid = create(client); tid = queued(factory, cid)
    size = int(os.environ.get('CHAT_CAPACITY_OUTPUT_MIB', '32'))*1024*1024
    block_size = 48000; expected = hashlib.sha256(); started = time.monotonic()
    for offset in range(0,size,block_size):
        prefix = f'{offset:016d}'.encode(); length = min(block_size,size-offset)
        block = (prefix+b'y'*block_size)[:length]; expected.update(block)
        with factory() as db:
            content_store.result(db,cid,tid,'output','capacity',offset,block); db.commit()
    saved = time.monotonic()-started; observed=hashlib.sha256(); cursor=None; total=0
    while True:
        response=client.get(f'/api/v1/chat/turns/{tid}/results',params={'cursor':cursor} if cursor else {})
        assert response.status_code==200
        page=response.json()['data']
        for item in page['items']:
            data=item['text'].encode();observed.update(data);total+=len(data)
        cursor=page['next_cursor']
        if not cursor:break
    assert total==size and observed.digest()==expected.digest()
    peak=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if __import__('sys').platform!='darwin':peak*=1024
    print('CAPACITY_RESULT',json.dumps({'bytes':size,'save_seconds':round(saved,3),'peak_rss_bytes':peak,'synthetic':True}))
    assert peak<=512*1024*1024
    if size==32*1024*1024:assert saved<=60
