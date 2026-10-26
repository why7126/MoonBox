"""Standalone synthetic probe for a fixed-resource, disposable deployment container."""
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import sys
import tempfile
import time
from sqlalchemy import create_engine, insert, select, text, func
from sqlalchemy.orm import sessionmaker
from app.chat import service, content_store, snapshot_store, result_reader
from app.chat.schema import migrate, conversations, turns
from app.chat.content_schema import entries


def main():
    count = int(os.environ.get('CHAT_CAPACITY_FILES', '12000'))
    output_size = int(os.environ.get('CHAT_CAPACITY_OUTPUT_MIB', '32')) * 1024**2
    with tempfile.TemporaryDirectory(prefix='chat-capacity-') as temporary:
        root = Path(temporary); workspace = root/'work'; workspace.mkdir()
        free = shutil.disk_usage(root).free
        assert free >= 20*1024**3, 'capacity environment needs 20 GiB free'
        engine = create_engine('sqlite:///'+str(root/'probe.db'))
        with engine.begin() as db:
            db.execute(text('CREATE TABLE admin_users (id VARCHAR(64) PRIMARY KEY)'))
            db.execute(text('CREATE TABLE admin_spaces (id VARCHAR(64) PRIMARY KEY, name VARCHAR(80), owner_id VARCHAR(64), status VARCHAR(24), deleted_at VARCHAR(32), expires_at VARCHAR(32))'))
            db.execute(text('CREATE TABLE admin_space_members (id VARCHAR(64) PRIMARY KEY, space_id VARCHAR(64), user_id VARCHAR(64), role VARCHAR(32))'))
            db.execute(text("INSERT INTO admin_users VALUES ('probe')"))
            db.execute(text("INSERT INTO admin_spaces (id,owner_id,status) VALUES ('probe','probe','ACTIVE')"))
        migrate(engine); factory = sessionmaker(engine)
        cid=service.identity(); tid=service.identity()
        os.environ['MOONBOX_CHAT_REPOSITORIES']='[{"id":"probe","space_id":"probe"}]'
        with factory() as db:
            db.execute(insert(conversations).values(**cid, owner_id='probe',space_id='probe',repository_id='probe',title='synthetic capacity'))
            db.execute(insert(turns).values(**tid,conversation_id=cid['id'],client_request_id='probe',status='running',prompt='synthetic capacity'))
            db.commit()
        size=52429
        for index in range(count):
            prefix=f'{index:016d}'.encode()
            (workspace/f'f{index:06d}.txt').write_bytes(prefix+b'x'*(size-len(prefix)))
        start=time.monotonic(); version=snapshot_store.capture(factory,cid['id'],tid['id'],workspace,'before')
        scan=time.monotonic()-start
        with factory() as db:
            observed=db.scalar(select(func.count()).select_from(entries).where(entries.c.version_id==version['version_id']))
        assert observed==count
        print(json.dumps({'stage':'snapshot','files':count,'bytes':count*size,'seconds':round(scan,3)}),flush=True)
        expected=hashlib.sha256();start=time.monotonic()
        for offset in range(0,output_size,48000):
            payload=(f'{offset:016d}'.encode()+b'y'*48000)[:min(48000,output_size-offset)];expected.update(payload)
            with factory() as db:
                content_store.result(db,cid['id'],tid['id'],'output','probe',offset,payload);db.commit()
        save=time.monotonic()-start;observed=hashlib.sha256();cursor=None;latencies=[];total=0
        while True:
            start=time.monotonic()
            with factory() as db: page=result_reader.results(db,'probe',tid['id'],cursor=cursor)
            latencies.append(time.monotonic()-start)
            for item in page['items']:
                payload=item['text'].encode();observed.update(payload);total+=len(payload)
            cursor=page['next_cursor']
            if not cursor:break
        peak=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*(1 if sys.platform=='darwin' else 1024)
        p95=sorted(latencies)[int((len(latencies)-1)*.95)]
        assert total==output_size and observed.digest()==expected.digest()
        report={'synthetic':True,'files':count,'snapshot_bytes':count*size,'snapshot_seconds':round(scan,3),
            'output_bytes':output_size,'save_seconds':round(save,3),'page_p95_seconds':round(p95,4),
            'peak_rss_bytes':peak,'free_bytes_at_start':free,'sqlite_version':__import__('sqlite3').sqlite_version}
        print(json.dumps(report),flush=True)
        assert peak<=512*1024**2 and p95<=1
        if count==12000:assert scan<=180
        if output_size==32*1024**2:assert save<=60
        engine.dispose()


if __name__=='__main__':main()
