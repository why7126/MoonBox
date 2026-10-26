"""Read-only checks of measured, sanitized REQ-0053 samples (never fabricate samples)."""
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[3]
EVIDENCE=ROOT/'openspec/changes/update-chat-scalable-execution-storage/evidence'


def measured(name):
    value=json.loads((EVIDENCE/name).read_text())
    for path,digest in value.get('source_hashes',{}).items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest, f'stale measured source: {path}'
    return value


def main(mode):
    if mode=='capacity':
        a,b=measured('capacity-small.json'),measured('capacity-large.json')
        assert a['files']==12000 and b['files']==48000
        assert a['snapshot_bytes']>=600*1024**2 and b['snapshot_bytes']>=2400*1024**2
        assert a['output_bytes']==32*1024**2 and b['output_bytes']==128*1024**2
        assert a['snapshot_seconds']<=180 and a['save_seconds']<=60
        assert b['peak_rss_bytes']-a['peak_rss_bytes']<=64*1024**2
        for value in (a,b):
            assert value['environment']['worker_memory_gib']==1
            assert value['peak_rss_bytes']<=512*1024**2 and value['page_p95_seconds']<=1
            assert value['free_bytes_at_start']>=20*1024**3
    elif mode=='live':
        value=measured('live-rounds.json')
        assert value['real_model'] and value['runtime_removed']
        assert {item['recovered'] for item in value['rounds']}=={False,True}
        for item in value['rounds']:
            assert item['status']=='completed' and item['fresh_process_read_matches'] and item['reread_matches']
            assert item['committed_sequence']>0 and len(item['result_sha256'])==64
            if item['recovered']: assert item['attempt_id']
    elif mode=='resource':
        value=measured('resource-protection.json')
        assert value['oom_killed'] and value['container_exit_code']==137
        assert value['healthy_fraction']>=.99 and value['sample_count']>=100 and value['max_read_seconds']<=2
        assert value['memory_gib']==1 and value['swap_gib']==0
        pids=measured('pid-protection.json')
        assert pids['refused'] and 0<pids['children']<128
    elif mode=='api':
        import runpy
        checker=runpy.run_path(str(ROOT/'scripts/validate-api-standard.py'))
        checker['check_router_file'](ROOT/'src/backend/app/chat/api.py')
        changed={'result_page','file_page','file_content','file_blocks','recover_turn'}
        violations=[v for v in checker['violations'] if any(f'路由 {name} ' in v for name in changed)]
        assert not violations, violations
    elif mode=='visual_preflight':
        from urllib.request import urlopen
        assert Path('/Applications/Google Chrome.app').is_dir()
        with urlopen('http://127.0.0.1:39058/frame.html',timeout=3) as response: assert response.status==200
        with urlopen('http://127.0.0.1:39057/api/v1/chat/conversations/ui-completed/turns',timeout=3) as response:
            assert json.load(response)['data']['items'][0]['id']=='turn-completed'
    elif mode=='visual':
        for width in (1440,1024,390):
            for theme in ('light','dark'):
                for state in ('failed','stopped','unknown','completed','read_error'):
                    stem=f'{width}-{theme}-{state}'
                    text=(EVIDENCE/'visual'/f'{stem}.txt').read_text()
                    assert '"overflow":false' in text and f'"viewport":{width}' in text
                    assert '"fontSize":"14px"' in text and '"radius":"6px"' in text
                    assert (EVIDENCE/'visual'/f'{stem}.png').stat().st_size>1000
        review=(EVIDENCE/'visual-review.md').read_text()
        assert '30/30' in review and '隔离' in review and 'Esc' in review
    else: raise ValueError('unknown evidence mode')
    print(json.dumps({'evidence':mode,'status':'verified'},ensure_ascii=False))


if __name__=='__main__':main(sys.argv[1])
