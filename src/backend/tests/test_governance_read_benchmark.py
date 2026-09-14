"""BUG-0016：显式成功HTTP读取性能基线；不替代真实浏览器TTFB。"""
import importlib.util, json, sys, math, time, os, statistics
from pathlib import Path
import pytest
from test_chat import chat
from test_governance_scope import bind
from app.governance import snapshot, reader, scope
from app.services import requirement_center

def load(name, file):
    spec=importlib.util.spec_from_file_location(name,file); module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module

@pytest.mark.skipif(os.getenv("BUG_READ_BENCHMARK") != "1", reason="显式运行30次性能对照，需要保存的修复前模块")
def test_benchmark(chat,tmp_path,monkeypatch):
    baseline = Path(os.environ['BUG_READ_BASELINE_DIR'])
    client,factory=chat
    from sqlalchemy import text
    from app.api.v1 import requirement_center as api
    with factory() as db:
        for name,kind in [("code","TEXT"),("description","TEXT"),("member_count","INTEGER"),("created_at","TEXT")]:
            db.execute(text(f"ALTER TABLE admin_spaces ADD COLUMN {name} {kind}"))
        for name in ["username","nickname"]:
            db.execute(text(f"ALTER TABLE admin_users ADD COLUMN {name} TEXT"))
        db.execute(text("CREATE TABLE admin_space_products (space_id TEXT)"));db.commit()
    old_snapshot=load('baseline_snapshot',baseline / 'snapshot.py')
    old_legacy=load('baseline_legacy',baseline / 'requirement_center.py')
    old_reader=load('baseline_reader',baseline / 'reader.py')
    old_legacy._SCOPED_ROOT=requirement_center._SCOPED_ROOT
    originals={name:getattr(requirement_center,name) for name in ['_read_yaml','_frontmatter','_change_dir','_change_tasks','_change_document_names','_change_spec_paths']}
    old_reader.stable=old_snapshot.stable;old_reader.materialize=old_snapshot.materialize;old_reader.legacy=old_legacy
    source=Path(__file__).resolve().parents[3]
    frozen=snapshot.stable(source)
    with snapshot.materialize(frozen) as root:
        bind(monkeypatch,root)
        result={'files':len(frozen.files),'bytes':sum(map(len,frozen.files.values())),'revision':frozen.revision,'boundary':'ASGI HTTP路由、实时授权和数据库围栏；身份依赖为隔离测试账号，不含浏览器网络TTFB'}
        for label,cls in [('baseline',old_reader.ProjectReader),('optimized',reader.ProjectReader)]:
            result[label]={}
            monkeypatch.setattr(api,'ProjectReader',cls)
            for name,original in originals.items():
                monkeypatch.setattr(requirement_center,name,getattr(old_legacy,name) if label=='baseline' else original)
            for operation,args in [('build_requirement_center_context',()),('read_requirement_center_document',('BUG-0016-capture','capture.md'))]:
                samples=[]
                if os.getenv('BUG_BENCH_COLD'):
                    snapshot._validated.clear()
                    for directory, _, _ in snapshot._trees.values(): directory.cleanup()
                    snapshot._trees.clear()
                for i in range(1 if os.getenv("BUG_BENCH_COLD") else 31):
                    route = '/api/v1/requirement-center/context' if not args else '/api/v1/requirement-center/issues/BUG-0016-capture/documents/capture.md'
                    start=time.perf_counter()
                    response=client.get(route,params={'space_id':'space','repository_id':'repo'})
                    elapsed=(time.perf_counter()-start)*1000
                    assert response.status_code==200,response.text
                    samples.append(elapsed)
                warm=samples[1:] or samples
                result[label][operation]={'cold_ms':round(samples[0],2),'warm_n':len(warm),'p50_ms':round(statistics.median(warm),2),'p95_ms':round(sorted(warm)[math.ceil(.95*len(warm))-1],2),'samples_ms':[round(x,2) for x in warm]}
                print(label,operation,result[label][operation]['p95_ms'],flush=True)
        for operation in result['baseline']:
            result['optimized'][operation]['improvement']=round(1-result['optimized'][operation]['p95_ms']/result['baseline'][operation]['p95_ms'],4)
        Path(os.environ['BUG_READ_BENCHMARK_OUTPUT']).write_text(json.dumps(result,ensure_ascii=False,indent=2))
        if os.getenv('BUG_BENCH_COLD'): return
        assert all(row['improvement']>=.5 for row in result['optimized'].values()),result
