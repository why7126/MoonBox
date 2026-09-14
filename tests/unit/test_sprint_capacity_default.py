"""Sprint default/override and capacity gate regression."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('capacity_tool', Path(__file__).resolve().parents[2] / 'scripts/add-sprint-scope-item.py')
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)

class CapacityTests(unittest.TestCase):
    def lines(self, capacity=None, estimate=23):
        rows = [] if capacity is None else [f'capacity_person_days: {capacity}']
        return rows + ['scope_estimates:', '  - id: sample', '    story_points: 1', f'    estimated_person_days: {estimate}', 'capacity_gate:', '  capacity_person_days: 20', '  estimated_person_days: 1', '  capacity_usage: 0.05', '  status: pass', '  note: old']

    def test_default_ignores_nested_stale_capacity(self):
        rows = self.lines()
        tool.update_capacity(rows)
        self.assertIn('capacity_person_days: 30', rows)
        self.assertIn('  capacity_person_days: 30', rows)
        self.assertIn('fix_buffer_person_days: 7', rows)
        self.assertFalse(tool.update_capacity(rows))

    def test_explicit_existing_preserved(self):
        rows = self.lines(40)
        tool.update_capacity(rows)
        self.assertIn('capacity_person_days: 40', rows)

    def test_invalid_capacity_rejected(self):
        for value in ('0', '-1', 'nan', 'inf', 'invalid', ''):
            with self.subTest(value=value), self.assertRaises(ValueError):
                tool.update_capacity(self.lines(value))

    def test_hard_gate_does_not_mutate(self):
        rows = self.lines(20, 25)
        before = list(rows)
        with self.assertRaises(ValueError):
            tool.update_capacity(rows)
        self.assertEqual(rows, before)

    def test_exact_tolerance_is_allowed(self):
        rows = self.lines(20, 24)
        tool.update_capacity(rows)
        self.assertIn('capacity_usage: 1.2', rows)
        self.assertIn('  status: warning', rows)

if __name__ == '__main__':
    unittest.main()
