"""Check the current deployed navigation observations against approved absolute targets."""
from pathlib import Path
import json,statistics
p=Path(__file__).parent
rows=json.loads((p/'browser.json').read_text())['samples']
valid=[x for x in rows if x.get('route_upper_bound_ms') is not None]
assert len(valid)==10 and all(x['arrived'] for x in valid)
server=[x['server_ms'] for x in valid];route=[x['route_upper_bound_ms'] for x in valid]
result={'server_median_ms':statistics.median(server),'server_max_ms':max(server),'route_median_upper_ms':statistics.median(route),'route_max_upper_ms':max(route)}
passed=result['server_median_ms']<=2000 and max(server)<=4000 and result['route_median_upper_ms']<=2500 and max(route)<=4500
print(json.dumps({'status':'passed' if passed else 'failed','reason':'deployed-navigation-targets','observed':result}))
raise SystemExit(0 if passed else 1)
