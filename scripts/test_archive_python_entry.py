"""Execute real archive shell against isolated gate/CLI stand-ins, never project data."""
import json
import os
from pathlib import Path
import re
import runpy
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ArchiveEntryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='archive entry ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        scripts = self.root / 'scripts'
        scripts.mkdir()
        for name in ('archive-change.sh', 'project-python.sh', 'project_python_preflight.py'):
            shutil.copyfile(ROOT / 'scripts' / name, scripts / name)
        self.env = dict(os.environ)
        for key in ('PYTHON_BIN', 'PYTHONPATH', 'FAIL_GATE'):
            self.env.pop(key, None)
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        self.env['PATH'] = str(self.bin) + os.pathsep + self.env['PATH']
        for name in ('python', 'python3'):
            self.executable(self.bin / name, '#!/bin/sh\necho wrong-python >&2\nexit 93\n')
        self.default = self.root / 'src/backend/.venv/bin/python'
        self.default.parent.mkdir(parents=True)
        self.executable(self.default, '#!/bin/sh\nexec ' + shlex.quote(sys.executable) + ' "$@"\n')
        self.active = self.root / 'openspec/changes/sample-change'
        self.active.mkdir(parents=True)
        (self.active / 'acceptance-plan.json').write_text('{}')
        gate = '''import json, os, sys
from pathlib import Path
name=Path(sys.argv[0]).name
with Path('calls.jsonl').open('a') as f:
 f.write(json.dumps({'name':name,'selected':os.environ.get('PYTHON_BIN'),'executable':sys.executable})+'\\n')
if os.environ.get('FAIL_GATE') == name: sys.exit(8)
if name == 'archive-recovery-guard.py': print('normal')
elif name == 'extract-ai-usage.py': print(json.dumps({'status':'ok','usage_mode':'unavailable','command_run_count':1}))
'''
        for name in set(re.findall(r'(?:scripts|archive_scripts)/([\w-]+\.py)', (scripts / 'archive-change.sh').read_text())):
            (scripts / name).write_text(gate)
        (scripts / 'archive-tool-route.py').write_text("print('legacy')\n")
        collect = scripts / 'workflow_sync/collect.py'
        collect.parent.mkdir()
        collect.write_text("def resolve_sprint_id(*args, **kwargs): return 'sprint-014', None\n")
        self.executable(self.bin / 'openspec', '''#!/bin/sh
set -eu
mkdir -p openspec/changes/archive
mv "openspec/changes/$2" "openspec/changes/archive/$(date +%Y-%m-%d)-$2"
''')

    def executable(self, path, content):
        path.write_text(content)
        path.chmod(0o755)

    def run_archive(self):
        return subprocess.run(['bash', 'scripts/archive-change.sh', 'sample-change', '--finalize'],
                              cwd=self.root, env=self.env, capture_output=True, text=True)

    def assert_success(self, selected):
        result = self.run_archive()
        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        self.assertFalse(self.active.exists())
        self.assertFalse((self.root / 'openspec/changes/archive').exists())
        self.assertEqual(1, len(list((self.root / 'openspec/archive').glob('*-sample-change'))))
        calls = [json.loads(line) for line in (self.root / 'calls.jsonl').read_text().splitlines()]
        self.assertGreater(len(calls), 10)
        self.assertTrue(all(Path(c['selected']).resolve() == Path(selected).resolve() for c in calls))
        self.assertIn('sync-workflow-status.py', [c['name'] for c in calls])
        self.assertIn('"status": "ok"', result.stdout)  # pipeline and -c parsing ran

    def test_default_ignores_bad_path_and_runs_inline_pipeline(self):
        self.assert_success(str(self.default))

    def test_explicit_interpreter_inherited(self):
        self.env['PYTHON_BIN'] = sys.executable
        self.assert_success(sys.executable)

    def test_invalid_explicit_stops_without_fallback(self):
        self.env['PYTHON_BIN'] = '/missing/python'
        result = self.run_archive()
        self.assertEqual(2, result.returncode)
        self.assertFalse((self.root / 'calls.jsonl').exists())
        self.assertFalse((self.root / 'openspec/archive').exists())
        self.assertTrue(self.active.exists())

    def test_missing_default_stops_before_gates(self):
        self.default.unlink()
        self.assertEqual(2, self.run_archive().returncode)
        self.assertFalse((self.root / 'calls.jsonl').exists())

    def test_missing_dependency_stops_before_gates(self):
        (self.root / 'scripts/yaml.py').write_text('raise ImportError("fixture")\n')
        self.assertEqual(2, self.run_archive().returncode)
        self.assertFalse((self.root / 'calls.jsonl').exists())

    def test_gate_failure_preserves_active_change(self):
        self.env['FAIL_GATE'] = 'validate-issue-acceptance-ready.py'
        self.assertNotEqual(0, self.run_archive().returncode)
        self.assertTrue(self.active.exists())
        self.assertFalse((self.root / 'openspec/archive').exists())

    def test_shell_regression_detection(self):
        validate = runpy.run_path(str(ROOT / 'scripts/validate-agent-context-budget.py'))['validate_governance_shell_python']
        path = self.root / 'scripts/archive-change.sh'
        original = path.read_text()
        self.assertEqual([], validate(self.root))
        for line in ('python scripts/check.py', 'python3 -c "pass"', 'value="$(python -c x)"',
                     'cat input | python -c x', 'python - <<\'PY\'\npass\nPY',
                     'exec python3 scripts/check.py', 'true; python scripts/check.py'):
            with self.subTest(line=line):
                path.write_text(original + '\n' + line + '\n')
                self.assertTrue(any('裸 Python' in e for e in validate(self.root)))
        path.write_text(original + '\n# python example\necho "python description"\ncat <<\'TEXT\'\npython documentation\nTEXT\n')
        self.assertEqual([], validate(self.root))
        path.write_text(original.replace('export PYTHON_BIN', '# omitted export'))
        self.assertTrue(validate(self.root))


if __name__ == '__main__':
    unittest.main()
