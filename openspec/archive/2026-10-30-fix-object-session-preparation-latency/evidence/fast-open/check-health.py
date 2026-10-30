from pathlib import Path
import json
r=json.loads((Path(__file__).parent/'health.json').read_text())
assert len(r['services'])==5 and all(x['status']=='running' and (x['health']=='healthy' or (name=='web' and x['health'] is None and r['web_http']==200)) for name,x in r['services'].items())
assert r['code_matches'] and r['web_manifest_matches'] and r['fixture_counts']=={'conversations':2,'turns':4}
print('Current deployment health, source manifest and unchanged fixture counts verified')
