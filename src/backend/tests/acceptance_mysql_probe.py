"""Real MySQL transaction/uniqueness checks in a disposable registered database."""
import os
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy import create_engine, insert, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from app.verification.acceptance_schema import TABLES, operations
from app.verification.acceptance_state import AcceptanceState, Conflict
from app.verification.acceptance_resources import reserve, release, GIB


def main():
    url=os.environ['ACCEPTANCE_TEST_DATABASE_URL']
    if not url.rsplit('/',1)[-1].startswith('acceptance_test_'):raise ValueError('test_database_required')
    engine=create_engine(url,pool_pre_ping=True)
    factory=sessionmaker(engine)
    with engine.connect() as db:
        version=db.scalar(text('SELECT VERSION()'))
        assert version.startswith('8.4.'),version
    for table in TABLES:table.create(engine,checkfirst=True)
    state=AcceptanceState(factory)
    def create():
        return state.create(actor='synthetic',space='synthetic-space',repository='synthetic-repo',
            conversation='synthetic-chat',turn='synthetic-turn',change='synthetic-change',
            request_key='concurrent-request',binding='b'*64,input_digest='a'*64,
            plan={'checks':[{'id':'AC-001','inputs':['src/test.py']}]})
    try:
        with ThreadPoolExecutor(max_workers=4) as pool:rows=list(pool.map(lambda _:create(),range(8)))
        assert len({row['id'] for row in rows})==1
        with factory() as db:assert len(db.execute(select(operations)).all())==1
        item=rows[0]
        def claim(index):
            try:return state.claim(item['id'],'worker-'+str(index))
            except Conflict:return None
        with ThreadPoolExecutor(max_workers=4) as pool:winners=[v for v in pool.map(claim,range(4)) if v]
        assert len(winners)==1
        token=winners[0]
        reservation=reserve(factory,token,available_cpu=16,available_memory=32*GIB,available_disk=100*GIB,hard_disk_limit=True)
        assert reservation['disk_bytes']==20*GIB
        state.result(token,'AC-001','passed',evidence={'kind':'database','digest':'d'*64})
        current=state.get(item['id']);state.cancel(item['id'],current['version'])
        try:state.heartbeat(token)
        except Conflict:pass
        else:raise AssertionError('cancelled_worker_renewed')
        state.cleanup(item['id'],released=False)
        current=state.get(item['id']);assert current['checks'][0]['status']=='passed' and not current['ready']
        release(factory,item['id'],resources_confirmed_absent=True)
        from app.chat.service import identity
        from app.verification.acceptance_schema import deliveries,archives,tool_waits
        for table,values in [
            (deliveries,dict(operation_id=item['id'],attempt_id=item['attempt_id'],input_digest='a'*64,state='queued')),
            (archives,dict(operation_id=item['id'],attempt_id=item['attempt_id'],digest='d'*64,relative_path='summary.json',manifest_json='{}',state='pending')),
            (tool_waits,dict(source_turn_id='synthetic-turn',call_id='call-test',generation=1,state='waiting'))]:
            with factory.begin() as db:db.execute(insert(table).values(**identity(),**values))
            try:
                with factory.begin() as db:db.execute(insert(table).values(**identity(),**values))
            except IntegrityError:pass
            else:raise AssertionError('duplicate_delivery_or_archive_allowed')
        print('MySQL '+version+': concurrent create/claim, bigint quotas, cancellation and evidence retention passed')
        print('Continuation, archive and tool-wait tables: duplicate identity rejected')
    finally:
        for table in reversed(TABLES):table.drop(engine)
        engine.dispose()


if __name__=='__main__':main()
