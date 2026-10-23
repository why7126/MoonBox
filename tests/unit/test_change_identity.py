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

    def test_hidden_system_directories_are_ignored(self):
        self.change('changes/add-governance')
        for name in ('.git', '.agents', '.codex'):
            (self.root / 'openspec' / 'changes' / name).mkdir()
        (self.root / 'openspec' / 'archive' / '.DS_Store').mkdir()
        self.assertEqual(module.validate(self.root), [])

    def test_archive_stops_before_openspec_or_moves(self):
        active = self.change('changes/add-governance')
        archived = self.change('archive/2026-09-01-add-governance')
        scripts = self.root / 'scripts'
        scripts.mkdir()
        for name in ('archive-change.sh', 'archive-recovery-guard.py', 'validate-change-identity.py', 'change_identity.py',
                     'validate-issue-acceptance-ready.py'):
            shutil.copy(ROOT / 'scripts' / name, scripts)
        # Wrapper lifecycle tests isolate admission; admission has its own integration suite.
        for gate in ('validate-issue-acceptance-ready.py', 'validate-change-delivery-evidence.py'):
            (scripts / gate).write_text('')
        binary = self.root / 'bin'
        binary.mkdir()
        cli = binary / 'openspec'
        cli.write_text('#!/bin/sh\ntouch openspec-was-called\n')
        cli.chmod(0o755)
        result = subprocess.run(['bash', 'scripts/archive-change.sh', 'add-governance', '2026-09-13'], cwd=self.root, env={**os.environ, 'PATH': str(binary)+os.pathsep+os.environ['PATH']}, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Change ID 重复 add-governance', result.stdout)
        self.assertFalse((self.root / 'openspec-was-called').exists())
        self.assertTrue(active.is_dir() and archived.is_dir())

    def archive_fixture(self, fail_validation=False):
        scripts = self.root / 'scripts'
        scripts.mkdir()
        shutil.copytree(ROOT / 'scripts/workflow_sync', scripts / 'workflow_sync')
        backend = self.root / 'src/backend'
        backend.mkdir(parents=True)
        (backend / 'app').symlink_to(ROOT / 'src/backend/app', target_is_directory=True)
        for name in ('archive-change.sh', 'archive-recovery-guard.py', 'validate-change-identity.py', 'change_identity.py',
                     'validate-issue-acceptance-ready.py'):
            shutil.copy(ROOT / 'scripts' / name, scripts)
        # Wrapper lifecycle tests isolate admission; admission has its own integration suite.
        for gate in ('validate-issue-acceptance-ready.py', 'validate-change-delivery-evidence.py'):
            (scripts / gate).write_text('')
        names = ('validate-directory-structure.py', 'validate-env-ignore-policy.py',
                 'validate-archive-evidence.py', 'sync-workflow-status.py',
                 'promote-issues-for-archive.py', 'extract-ai-usage.py')
        for name in names:
            code = "from pathlib import Path\nwith Path('steps').open('a') as f: f.write(%r + '\\n')\n" % name
            if fail_validation and name == 'validate-archive-evidence.py':
                code += 'raise SystemExit(1)\n'
            if name == 'extract-ai-usage.py':
                code += "print('{}')\n"
            (scripts / name).write_text(code)

    def test_half_archive_recovery_serially_finalizes_without_cli(self):
        self.archive_fixture()
        archived = self.change('archive/2026-09-01-add-governance', 'add-governance')
        result = subprocess.run(['bash', 'scripts/archive-change.sh', 'add-governance', '--finalize'],
                                cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(archived.exists())
        self.assertIn('without re-merging', result.stdout)
        self.assertEqual((self.root / 'steps').read_text().splitlines(), [
            'validate-directory-structure.py', 'validate-env-ignore-policy.py',
            'validate-archive-evidence.py', 'sync-workflow-status.py',
            'promote-issues-for-archive.py', 'extract-ai-usage.py'])

    def test_archive_usage_resolves_iteration_from_sprint_scope(self):
        self.archive_fixture()
        archived = self.change('archive/2026-09-01-add-governance', 'add-governance')
        (archived / 'trace.md').write_text('---\nchange_id: add-governance\niteration: sprint-011\n---\n')
        sprint = self.root / 'iterations/change/sprint-011'
        sprint.mkdir(parents=True)
        (sprint / 'sprint.yaml').write_text('id: sprint-011\nstatus: planning\nchanges:\n  - add-governance\n')
        hook = self.root / 'scripts/extract-ai-usage.py'
        hook.write_text("import sys,json\nfrom pathlib import Path\nPath('hook-args.json').write_text(json.dumps(sys.argv))\nprint('{}')\n")
        result = subprocess.run(['bash', 'scripts/archive-change.sh', 'add-governance', '--finalize'],
                                cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        import json
        args = json.loads((self.root / 'hook-args.json').read_text())
        self.assertEqual(args[args.index('--sprint') + 1], 'sprint-011')

    def test_half_archive_validation_failure_stops_before_sync(self):
        self.archive_fixture(fail_validation=True)
        self.change('archive/2026-09-01-add-governance', 'add-governance')
        result = subprocess.run(['bash', 'scripts/archive-change.sh', 'add-governance', '--finalize'],
                                cwd=self.root, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('sync-workflow-status.py', (self.root / 'steps').read_text())

    def test_active_archive_validates_directory_before_cli(self):
        self.archive_fixture()
        active = self.change('changes/add-governance', 'add-governance')
        (self.root / 'scripts/validate-directory-structure.py').write_text('raise SystemExit(1)\n')
        binary = self.root / 'bin'
        binary.mkdir()
        cli = binary / 'openspec'
        cli.write_text('#!/bin/sh\ntouch openspec-was-called\n')
        cli.chmod(0o755)
        result = subprocess.run(['bash', 'scripts/archive-change.sh', 'add-governance', '--finalize'],
                                cwd=self.root, env={**os.environ, 'PATH': str(binary)+os.pathsep+os.environ['PATH']},
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(active.exists())
        self.assertFalse((self.root / 'openspec-was-called').exists())

    def test_legacy_archive_move_survives_cross_device_error(self):
        self.archive_fixture()
        legacy = self.root / 'openspec/changes/archive/2026-09-01-add-governance'
        legacy.mkdir(parents=True)
        (legacy / 'trace.md').write_text('---\nchange_id: add-governance\n---\n')
        injected = self.root / 'injected'
        injected.mkdir()
        (injected / 'sitecustomize.py').write_text(
            "import errno, os\noriginal = os.rename\ndef rename(source, target, *args, **kwargs):\n"
            "    if '/changes/archive/' in str(source): raise OSError(errno.EXDEV, 'cross-device')\n"
            "    return original(source, target, *args, **kwargs)\nos.rename = rename\n")
        # Identity validation normally blocks the legacy root before migration;
        # isolate the move behavior while keeping all following gates enabled.
        (self.root / 'scripts/validate-change-identity.py').write_text('')
        result = subprocess.run(['bash', 'scripts/archive-change.sh', 'add-governance'], cwd=self.root,
            env={**os.environ, 'PYTHONPATH': str(injected)}, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(legacy.exists())
        self.assertTrue((self.root / 'openspec/archive/2026-09-01-add-governance/trace.md').is_file())

    def test_merge_completed_before_move_retries_with_skip_specs(self):
        self.archive_fixture()
        self.change('changes/add-governance', 'add-governance')
        specs = self.root / 'openspec/specs/example'
        specs.mkdir(parents=True)
        (specs / 'spec.md').write_text('base\n')
        binary = self.root / 'bin'
        binary.mkdir()
        cli = binary / 'openspec'
        cli.write_text("""#!/usr/bin/env python3
from pathlib import Path
import shutil
import sys
spec = Path('openspec/specs/example/spec.md')
preview = 'moonbox-archive-preview-' in str(Path.cwd())
if '--skip-specs' not in sys.argv:
    spec.write_text(spec.read_text() + 'merged\\n')
if not preview and not Path('failed-once').exists():
    Path('failed-once').write_text('1')
    raise SystemExit(1)
if not preview:
    Path('retry-args').write_text(' '.join(sys.argv))
source = Path('openspec/changes/add-governance')
target = Path('openspec/changes/archive/2026-09-01-add-governance')
target.parent.mkdir(parents=True, exist_ok=True)
shutil.move(source, target)
""")
        cli.chmod(0o755)
        env = {**os.environ, 'PATH': str(binary) + os.pathsep + os.environ['PATH']}
        command = ['bash', 'scripts/archive-change.sh', 'add-governance', '2026-09-01']
        first = subprocess.run(command, cwd=self.root, env=env, capture_output=True, text=True)
        self.assertNotEqual(first.returncode, 0)
        self.assertEqual((specs / 'spec.md').read_text(), 'base\nmerged\n')
        self.assertTrue((self.root / 'openspec/changes/add-governance').is_dir())
        retry = subprocess.run(command, cwd=self.root, env=env, capture_output=True, text=True)
        self.assertEqual(retry.returncode, 0, retry.stdout + retry.stderr)
        self.assertIn('--skip-specs', (self.root / 'retry-args').read_text())
        self.assertEqual((specs / 'spec.md').read_text(), 'base\nmerged\n')
        self.assertTrue((self.root / 'openspec/archive/2026-09-01-add-governance').is_dir())

    def test_unknown_edit_after_merge_blocks_and_preserves_files(self):
        self.archive_fixture()
        self.change('changes/add-governance', 'add-governance')
        specs = self.root / 'openspec/specs/example'
        specs.mkdir(parents=True)
        (specs / 'spec.md').write_text('base\n')
        binary = self.root / 'bin'
        binary.mkdir()
        cli = binary / 'openspec'
        cli.write_text("""#!/usr/bin/env python3
from pathlib import Path
spec = Path('openspec/specs/example/spec.md')
spec.write_text(spec.read_text() + 'merged\\n')
if 'moonbox-archive-preview-' not in str(Path.cwd()):
    raise SystemExit(1)
import shutil
source = Path('openspec/changes/add-governance')
target = Path('openspec/changes/archive/2026-09-01-add-governance')
target.parent.mkdir(parents=True)
shutil.move(source, target)
""")
        cli.chmod(0o755)
        env = {**os.environ, 'PATH': str(binary) + os.pathsep + os.environ['PATH']}
        command = ['bash', 'scripts/archive-change.sh', 'add-governance', '2026-09-01']
        first = subprocess.run(command, cwd=self.root, env=env, capture_output=True, text=True)
        self.assertNotEqual(first.returncode, 0)
        (specs / 'spec.md').write_text('base\nmerged\nexternal\n')
        retry = subprocess.run(command, cwd=self.root, env=env, capture_output=True, text=True)
        self.assertNotEqual(retry.returncode, 0)
        self.assertIn('ARCHIVE_RECOVERY_BLOCKED', retry.stderr)
        self.assertEqual((specs / 'spec.md').read_text(), 'base\nmerged\nexternal\n')
        self.assertTrue((self.root / 'openspec/changes/add-governance').is_dir())
        self.assertTrue((self.root / 'openspec/archive/.archive-recovery/add-governance.json').is_file())


if __name__ == '__main__':
    unittest.main()
