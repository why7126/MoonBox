import sys
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
from workflow_sync.initialization import initialize

class InitializationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.path = self.root / 'openspec/changes/test-change/trace.md'
        self.path.parent.mkdir(parents=True)
        self.record = SimpleNamespace(change_id='test-change', location='active', tasks=SimpleNamespace(done=0))
    def test_dry_run_and_idempotency(self):
        result = initialize(self.root, self.record)
        self.assertFalse(self.path.exists())
        self.assertIsNone(result['execution']['started_at'])
        initialize(self.root, self.record, write=True)
        before = self.path.read_bytes()
        initialize(self.root, self.record, write=True)
        self.assertEqual(before, self.path.read_bytes())
    def test_progress_without_trace_blocks(self):
        self.record.tasks.done = 1
        with self.assertRaises(ValueError): initialize(self.root, self.record, write=True)
        self.assertFalse(self.path.exists())
    def test_invalid_status_blocks(self):
        self.path.write_text('---\nstatus: invalid\n---\n')
        with self.assertRaises(ValueError): initialize(self.root, self.record, write=True)
    def test_legacy_and_issue_source_preserved(self):
        self.path.write_text('---\nstatus: applied\nrequirement_id: REQ-0001-example\n---\n历史正文')
        before = self.path.read_bytes()
        initialize(self.root, self.record, write=True)
        self.assertEqual(before, self.path.read_bytes())
    def test_conflicting_execution_blocks(self):
        initialize(self.root, self.record, write=True)
        self.path.write_text(self.path.read_text().replace('status: proposed','status: applied'))
        with self.assertRaises(ValueError): initialize(self.root, self.record, write=True)
    def test_symlink_blocks(self):
        other=self.root/'other';other.write_text('private')
        self.path.symlink_to(other)
        with self.assertRaises(ValueError): initialize(self.root, self.record, write=True)

if __name__ == '__main__': unittest.main()
