"""Conflict fixtures exercise cross-lifecycle identity and archive preflight."""
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('change_identity', ROOT / 'scripts/change_identity.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for folder in ('changes', 'archive'):
            (self.root / 'openspec' / folder).mkdir(parents=True)

    def change(self, path, cid=None):
        directory = self.root / 'openspec' / path
        directory.mkdir()
        if cid:
            (directory / 'trace.md').write_text(f'---\nchange_id: {cid}\n---\n')
        return directory

    def test_distinct_initial_and_enhancement(self):
        self.change('archive/2026-09-01-add-governance', 'add-governance')
        self.change('archive/2026-09-02-enhance-governance', 'enhance-governance')
        self.assertEqual(module.validate(self.root), [])

    def test_two_archive_dates_conflict(self):
        self.change('archive/2026-09-01-add-governance')
        self.change('archive/2026-09-02-add-governance')
        errors = module.validate(self.root)
        self.assertEqual(len(errors), 1)
        self.assertIn('2026-09-01', errors[0])
        self.assertIn('2026-09-02', errors[0])

    def test_active_archive_conflict(self):
        self.change('changes/add-governance')
        self.change('archive/2026-09-01-add-governance')
        self.assertIn('重复', module.validate(self.root)[0])

    def test_new_id_cannot_reuse_archive(self):
        self.change('archive/2026-09-01-add-governance')
        self.assertIn('已占用', module.validate(self.root, 'add-governance')[0])
        self.assertEqual(module.validate(self.root, 'enhance-governance'), [])

    def test_metadata_mismatch(self):
        self.change('changes/enhance-governance', 'add-governance')
        self.assertIn('不一致', module.validate(self.root)[0])

    def test_metadata_legacy_without_id_allowed(self):
        self.change('changes/add-governance')
        self.assertEqual(module.validate(self.root), [])

    def test_archive_stops_before_openspec_or_moves(self):
        active = self.change('changes/add-governance')
        archived = self.change('archive/2026-09-01-add-governance')
        scripts = self.root / 'scripts'
        scripts.mkdir()
        for name in ('archive-change.sh', 'validate-change-identity.py', 'change_identity.py'):
            shutil.copy(ROOT / 'scripts' / name, scripts)
        binary = self.root / 'bin'
        binary.mkdir()
        cli = binary / 'openspec'
        cli.write_text('#!/bin/sh\ntouch openspec-was-called\n')
        cli.chmod(0o755)
        result = subprocess.run(['bash', 'scripts/archive-change.sh', 'add-governance', '2026-09-13'], cwd=self.root, env={**os.environ, 'PATH': str(binary)+os.pathsep+os.environ['PATH']}, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('重复', result.stdout)
        self.assertFalse((self.root / 'openspec-was-called').exists())
        self.assertTrue(active.is_dir() and archived.is_dir())


if __name__ == '__main__':
    unittest.main()
