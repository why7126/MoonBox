"""Isolated launcher regression tests; never mutate project workflow data."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class EntryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='python entry ')
        self.root = Path(self.temp.name)
        (self.root / 'scripts').mkdir()
        for name in ('project-python.sh', 'project_python_preflight.py'):
            shutil.copy(ROOT / 'scripts' / name, self.root / 'scripts' / name)
        self.env = dict(os.environ)
        self.env.pop('PYTHON_BIN', None)
        self.env.pop('PYTHONPATH', None)
        (self.root / 'scripts' / 'target.py').write_text(
            'import sys, subprocess, os\n'
            'from pathlib import Path\n'
            'Path("ran").write_text("yes")\n'
            'assert subprocess.check_output([sys.executable, "-c", '
            '"import sys; print(sys.executable)"], text=True).strip() == sys.executable\n'
            'assert os.environ["PYTHON_BIN"] == sys.executable\n'
            'print(repr(sys.argv[1:]))\n'
            'sys.exit(7)\n')

    def tearDown(self):
        self.temp.cleanup()

    def run_entry(self, *args):
        return subprocess.run(['bash', str(self.root / 'scripts/project-python.sh'), *args],
                              cwd=self.root, env=self.env, capture_output=True, text=True)

    def test_missing_default_stops_before_write(self):
        result = self.run_entry('scripts/target.py')
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.root / 'ran').exists())

    def test_invalid_explicit_does_not_fallback(self):
        self.install_default()
        for value in ('', '/missing/python'):
            self.env['PYTHON_BIN'] = value
            self.assertEqual(self.run_entry('scripts/target.py').returncode, 2)
        self.assertFalse((self.root / 'ran').exists())

    def install_default(self):
        binary = self.root / 'src/backend/.venv/bin/python'
        binary.parent.mkdir(parents=True)
        # A launcher, not a symlink: preserve the real venv prefix.
        import shlex
        binary.write_text('#!/bin/sh\nexec ' + shlex.quote(sys.executable) + ' "$@"\n')
        binary.chmod(0o755)

    def test_default_check_with_space_path(self):
        self.install_default()
        self.assertEqual(self.run_entry('--check').returncode, 0)
        self.assertFalse((self.root / 'ran').exists())

    def test_explicit_arguments_exit_and_inheritance(self):
        self.env['PYTHON_BIN'] = sys.executable
        result = self.run_entry('scripts/target.py', 'a b', '$(literal)', '--flag')
        self.assertEqual(result.returncode, 7, result.stderr)
        self.assertIn("['a b', '$(literal)', '--flag']", result.stdout)

    def test_missing_dependency_stops_before_write(self):
        self.env['PYTHON_BIN'] = sys.executable
        (self.root / 'scripts/yaml.py').write_text('raise ImportError("isolated missing yaml")\n')
        result = self.run_entry('scripts/target.py')
        self.assertEqual(result.returncode, 2)
        self.assertIn('PyYAML unavailable', result.stderr)
        self.assertFalse((self.root / 'ran').exists())

    def test_version_guard(self):
        result = subprocess.run([sys.executable, '-c',
            'import runpy,sys; sys.version_info=(3,11); '
            'runpy.run_path("scripts/project_python_preflight.py",run_name="__main__")'],
            cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn('3.12', result.stderr)

    def test_non_root_cwd_and_absolute_script(self):
        self.env['PYTHON_BIN'] = sys.executable
        result = subprocess.run(['bash', str(self.root / 'scripts/project-python.sh'),
                                 str(self.root / 'scripts/target.py')], cwd=self.root / 'scripts',
                                env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 7, result.stderr)
        self.assertTrue((self.root / 'scripts/ran').exists())

    def test_skill_regression_guard(self):
        import runpy
        validator = runpy.run_path(str(ROOT / 'scripts/validate-agent-context-budget.py'))['validate_python_entry']
        skill = self.root / 'SKILL.md'
        for command in ('python scripts/example.py', 'python3 scripts/example.py'):
            skill.write_text(command)
            self.assertTrue(validator(skill))
        skill.write_text('bash scripts/project-python.sh scripts/example.py')
        self.assertEqual(validator(skill), [])


if __name__ == '__main__':
    unittest.main()
