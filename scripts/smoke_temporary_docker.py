"""独立 Docker 实测；仅创建和回收本脚本登记样本，不拉取镜像。"""
import argparse
import contextlib
import io
import json
from unittest.mock import patch

import temporary_docker as td


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', required=True, help='已有且提供 /bin/sh 的本地镜像')
    args = parser.parse_args()
    image = json.loads(td.docker('image', 'inspect', args.image))[0]
    if image.get('Config', {}).get('Volumes'):
        raise td.GuardError('smoke_image_has_volumes')
    records = []
    try:
        for index in range(2):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                if td.main(['register', '--change', 'add-temporary-docker-lifecycle', '--purpose', 'smoke']):
                    raise td.GuardError('smoke_register_failed')
            record = td.load(td.REGISTRY, json.loads(output.getvalue())['run'])
            records.append(record)
            flags = [arg for key, value in td.labels(record).items() for arg in ['--label', key + '=' + value]]
            if index == 0:
                td.docker('network', 'create', *flags, 'moonbox-temp-' + record['run'])
            td.docker('container', 'create', '--name', 'moonbox-temp-' + record['run'],
                      *flags, '--network', 'none', '--read-only', '--cap-drop', 'ALL',
                      '--security-opt', 'no-new-privileges', '--memory', '64m', '--pids-limit', '16',
                      '--entrypoint', '/bin/sh', image['Id'], '-c', 'sleep 60')
            if index == 0:
                td.docker('container', 'start', 'moonbox-temp-' + record['run'])
        with td.locked(td.REGISTRY):
            assert td.reconcile(td.REGISTRY, records[0])['status'] == 'preview'
            assert td.reconcile(td.REGISTRY, records[0], check=True)['status'] == 'remaining'
            assert td.reconcile(td.REGISTRY, records[0], apply=True)['status'] == 'clean'
            assert td.reconcile(td.REGISTRY, records[1], check=True)['status'] == 'remaining'
            # Real Docker deletion with a simulated future clock; not a real TTL wait.
            with patch.object(td.time, 'time', return_value=records[1]['expires'] + 1):
                assert td.reconcile(td.REGISTRY, records[1], expired_only=True, apply=True)['status'] == 'clean'
            for record in records:
                assert td.reconcile(td.REGISTRY, record, apply=True)['status'] == 'clean'
                assert td.reconcile(td.REGISTRY, record, check=True)['status'] == 'clean'
        print(json.dumps({'status': 'passed', 'runs': 2, 'containers': 2, 'networks': 1,
                          'remaining': 0, 'expiry_clock': 'simulated', 'docker': 'real'}))
    finally:
        failures = []
        with td.locked(td.REGISTRY):
            for record in records:
                try:
                    td.reconcile(td.REGISTRY, record, apply=True)
                except td.GuardError:
                    failures.append(record['run'])
        if failures:
            raise td.GuardError('smoke_cleanup_failed:' + ','.join(failures))


if __name__ == '__main__':
    main()
