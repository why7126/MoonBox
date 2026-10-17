"""Chat shell marker only exempts exact empty temporary tool directories."""

import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[2] / 'scripts/runtime_tool_mounts.py'
spec = importlib.util.spec_from_file_location('runtime_tool_mounts', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class RuntimeToolMountTests(unittest.TestCase):
    def test_repository_scan_covers_nested_paths_and_excludes_dependency_trees(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / '.agents/skills').mkdir(parents=True)
            nested = root / '.agents/skills/example/.codex'
            nested.mkdir(parents=True)
            expected = root / 'docs/spec-logs/.codex'
            expected.mkdir(parents=True)
            (root / 'openspec/specs/.agents').mkdir(parents=True)
            (root / 'src/backend/.venv/lib/fastapi/.agents').mkdir(parents=True)
            (root / 'src/web/node_modules/pkg/.codex').mkdir(parents=True)
            (root / 'data/runtime/.agents').mkdir(parents=True)
            sample = root / 'data/samples/.codex'
            sample.mkdir(parents=True)
            found = set(module.repository_tool_paths(root))
            self.assertEqual(found, {expected.resolve(), nested.resolve(), sample.resolve(),
                                     (root / 'openspec/specs/.agents').resolve()})

    def test_exact_empty_path_requires_chat_shell_marker(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'work'
            path = root / 'issues/.agents'
            other = root / 'issues/.unknown'
            path.mkdir(parents=True)
            other.mkdir()
            check = lambda item: module.is_ephemeral_tool_mount(root, item, executor_root=root)
            with patch.dict(module.os.environ, {}, clear=True):
                self.assertFalse(check(path))
            with patch.dict(module.os.environ, {'MOONBOX_CHAT_TOOL_SANDBOX': '1'}, clear=True):
                self.assertTrue(check(path))
                self.assertFalse(check(other))
                mounted = root / 'openspec/specs/.codex'
                mounted.mkdir(parents=True)
                self.assertTrue(check(mounted))
                (path / 'content').write_text('must fail')
                self.assertFalse(check(path))

    def test_symlink_never_gets_exemption(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / 'work'
            target = root / 'target'
            target.mkdir(parents=True)
            link = root / 'issues/.agents'
            link.parent.mkdir()
            link.symlink_to(target, target_is_directory=True)
            with patch.dict(module.os.environ, {'MOONBOX_CHAT_TOOL_SANDBOX': '1'}):
                self.assertFalse(module.is_ephemeral_tool_mount(root, link, executor_root=root))


if __name__ == '__main__':
    unittest.main()
