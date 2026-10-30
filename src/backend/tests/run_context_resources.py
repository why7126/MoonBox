"""Explicit BUG-0056 container runner: eight isolated 30-minute workloads.

Requires /work/fixture, /baseline, /work/deps, and /results in the registered
temporary container. Never imported by the application or normal pytest run.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

def main():
    results = {}
    jobs = []
    modes = os.environ.get('CONTEXT_RESOURCE_MODES', 'baseline,optimized').split(',')
    if not modes or any(mode not in ('baseline', 'optimized') for mode in modes):
        raise ValueError('invalid resource modes')
    for concurrency in (1, 4):
        for scale in ('reference', 'expanded'):
            for mode in modes:
                name = f'resource-{scale}-{concurrency}-{mode}'
                env = {**os.environ, 'CONTEXT_RESOURCE_TEST': '1',
                       'CONTEXT_RESOURCE_MODE': mode, 'CONTEXT_RESOURCE_SCALE': scale,
                       'CONTEXT_RESOURCE_CONCURRENCY': str(concurrency),
                       'CONTEXT_RESOURCE_SECONDS': '1800',
                       'CONTEXT_RESOURCE_OUTPUT': '/results/' + name + '.json',
                       'BUG_READ_SOURCE': os.environ.get('BUG_READ_SOURCE', '/work/fixture'),
                       'BUG_READ_BASELINE_DIR': '/baseline',
                       'PYTHONPATH': os.environ.get('PYTHONPATH', '/work/deps:/work')}
                log = open('/results/' + name + '.txt', 'w')
                process = subprocess.Popen([sys.executable, '-m', 'pytest', '-q',
                                            'tests/test_context_resources.py'], env=env, stdout=log, stderr=log)
                jobs.append((name, process, log))
    print(f'Started {len(jobs)} isolated 1800-second workloads; shared 4 vCPU / 8 GiB stress envelope.', flush=True)
    while jobs:
        remaining = []
        for name, process, log in jobs:
            code = process.poll()
            if code is None:
                remaining.append((name, process, log))
                continue
            log.close()
            results[name] = code
            print(name + ': exit ' + str(code), flush=True)
            Path('/results/resource-exits.json').write_text(json.dumps(results, indent=2))
        jobs = remaining
        if jobs:
            time.sleep(5)
    sys.exit(int(any(results.values())))


if __name__ == "__main__":
    main()
