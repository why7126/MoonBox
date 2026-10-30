from pathlib import Path
import json,statistics
p=Path(__file__).parent
r=json.loads((p/'browser-samples.json').read_text())
assert len(r)==10 and all(x['chat'] and x['draft'] for x in r)
t=[x['route_observed_upper_ms'] for x in r]
assert statistics.median(t)<=2500 and max(t)<=4500
print(json.dumps({'navigation':'passed','median_upper_ms':statistics.median(t),'max_upper_ms':max(t),'full_write_matrix':'not_currently_resampled'}))
