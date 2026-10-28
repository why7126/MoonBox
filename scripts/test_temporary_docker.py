"""临时 Docker 回收边界回归；使用内存 Docker，不操作真实环境。"""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import temporary_docker as td


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.record = dict(schema_version=1, run='a' * 32, daemon='d' * 64,
                           created=100, expires=200, status='open')
        self.containers = [{'Id': 'b' * 64, 'Config': {'Labels': td.labels(self.record)},
                            'State': {'Running': False}, 'Mounts': []}]
        self.networks = [{'Id': 'c' * 64, 'Labels': td.labels(self.record), 'Containers': {}}]
        self.calls = []
        self.addCleanup(patch.stopall)
        patch.object(td, 'daemon', return_value='d' * 64).start()
        patch.object(td, 'docker', side_effect=self.docker).start()
        td.save(self.folder, self.record)

    def docker(self, *args):
        self.calls.append(args)
        if args[0] == 'ps':
            return '\n'.join(c['Id'] for c in self.containers)
        if args[:2] == ('network', 'ls'):
            return '\n'.join(n['Id'] for n in self.networks)
        items = self.containers if args[0] == 'container' else self.networks
        if args[1] == 'inspect':
            return json.dumps([x for x in items if x['Id'] == args[2]])
        if args[1] == 'rm':
            items[:] = [x for x in items if x['Id'] != args[-1]]
            return args[-1]
        raise AssertionError(args)

    def reconcile(self, **kwargs):
        return td.reconcile(self.folder, self.record, **kwargs)

    def assert_no_delete(self):
        self.assertFalse(any('rm' in call for call in self.calls))

    def test_preview_does_not_remove(self):
        self.assertEqual(self.reconcile()['status'], 'preview')
        self.assert_no_delete()
        self.assertEqual(td.load(self.folder, self.record['run'])['status'], 'open')

    def test_cleanup_running_and_idempotent(self):
        self.containers[0]['State']['Running'] = True
        self.assertEqual(self.reconcile(apply=True)['status'], 'clean')
        self.assertEqual(self.reconcile(apply=True)['status'], 'clean')
        self.assertEqual(td.load(self.folder, self.record['run'])['status'], 'closed')

    def test_check_detects_remaining(self):
        self.assertEqual(self.reconcile(check=True)['status'], 'remaining')
        self.assert_no_delete()

    def test_expired_running_is_blocked(self):
        self.containers[0]['State']['Running'] = True
        with self.assertRaisesRegex(td.GuardError, 'expired_running'):
            self.reconcile(apply=True, expired_only=True)
        self.assert_no_delete()

    def test_reap_stopped_without_force(self):
        self.reconcile(apply=True, expired_only=True)
        self.assertFalse(any('--force' in call for call in self.calls))
        self.assertEqual(self.reconcile(check=True)['status'], 'clean')

    def test_not_due_is_preserved(self):
        with patch.object(td.time, 'time', return_value=150):
            self.assertEqual(self.reconcile(apply=True, expired_only=True)['status'], 'not_due')
        self.assert_no_delete()

    def test_wrong_daemon_refused(self):
        with patch.object(td, 'daemon', return_value='other'):
            with self.assertRaisesRegex(td.GuardError, 'daemon_mismatch'):
                self.reconcile(apply=True)
        self.assert_no_delete()

    def test_label_mismatch_refused(self):
        self.containers[0]['Config']['Labels'][td.PREFIX + 'managed'] = 'false'
        with self.assertRaisesRegex(td.GuardError, 'identity_mismatch'):
            self.reconcile(apply=True)
        self.assert_no_delete()

    def test_foreign_endpoint_refused(self):
        self.networks[0]['Containers'] = {'e' * 64: {}}
        with self.assertRaisesRegex(td.GuardError, 'foreign_endpoints'):
            self.reconcile(apply=True)
        self.assert_no_delete()

    def test_volume_refused(self):
        self.containers[0]['Mounts'] = [{'Type': 'volume'}]
        with self.assertRaisesRegex(td.GuardError, 'volume_requires'):
            self.reconcile(apply=True)
        self.assert_no_delete()

    def test_docker_failure_not_clean(self):
        with patch.object(td, 'docker', side_effect=td.GuardError('docker_command_failed:ps')):
            with self.assertRaises(td.GuardError):
                self.reconcile(check=True)

    def test_run_path_traversal_and_corrupt_record(self):
        with self.assertRaises(td.GuardError):
            td.load(self.folder, '../other')
        record = copy.deepcopy(self.record)
        record['expires'] = 'invalid'
        with self.assertRaises(td.GuardError):
            td.valid_record(record)

    def test_symlink_refused(self):
        (self.folder / (self.record['run'] + '.json')).unlink()
        (self.folder / (self.record['run'] + '.json')).symlink_to('/dev/null')
        with self.assertRaises(td.GuardError):
            td.load(self.folder, self.record['run'])

    def test_delete_failure_keeps_open(self):
        original = self.docker
        def fail(*args):
            if 'rm' in args:
                raise td.GuardError('docker_command_failed:container')
            return original(*args)
        with patch.object(td, 'docker', side_effect=fail):
            with self.assertRaises(td.GuardError):
                self.reconcile(apply=True)
        self.assertEqual(td.load(self.folder, self.record['run'])['status'], 'open')


if __name__ == '__main__':
    unittest.main()
