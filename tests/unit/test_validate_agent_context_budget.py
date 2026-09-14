"""Apply 治理契约的正例与故意退化反例。"""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('budget_validator', ROOT / 'scripts/validate-agent-context-budget.py')
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class ApplyContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.scope = patch.object(validator, 'ROOT', self.root)
        self.scope.start()
        self.addCleanup(self.scope.stop)
        for name in validator.APPLY_SKILLS:
            path = self.root / '.agents/skills' / name / 'SKILL.md'
            path.parent.mkdir(parents=True)
            path.write_text((ROOT / '.agents/skills' / name / 'SKILL.md').read_text())
        script = self.root / "scripts/validate-apply-behavior.py"
        script.parent.mkdir(parents=True)
        script.write_text((ROOT / "scripts/validate-apply-behavior.py").read_text())
        self.doc = self.root / validator.APPLY_CONTRACT_DOC
        self.doc.parent.mkdir(parents=True)
        self.doc.write_text((ROOT / validator.APPLY_CONTRACT_DOC).read_text())

    def test_current_skills_and_source_pass(self):
        self.assertEqual(validator.validate_apply_contract_source(), [])
        for path in self.root.glob('.agents/skills/*/SKILL.md'):
            self.assertEqual(validator.validate_apply_execution_contract(path), [])

    def test_missing_reference_is_rejected_for_both_entries(self):
        for path in self.root.glob('.agents/skills/*/SKILL.md'):
            with self.subTest(skill=path.parent.name):
                path.write_text(path.read_text().replace(validator.APPLY_CONTRACT_REFERENCE, 'missing.md'))
                self.assertTrue(validator.validate_apply_execution_contract(path))

    def test_known_pause_completion_and_modify_regressions_are_rejected(self):
        old_lines = [
            'Stop and ask if task is ambiguous, gate is blocked.',
            'Task is unclear → ask for clarification',
            'If task is ambiguous, pause and ask before implementing',
            'If implementation reveals issues, pause and suggest artifact updates',
            'Implementation reveals a design issue → suggest updating artifacts',
            'Error or blocker encountered → report and wait for guidance',
            "Pause on errors, blockers, or unclear requirements - don't guess",
            'If `state: "all_done"`: congratulate, suggest archive',
            'All tasks complete! Ready to archive this change.',
            'keep the task unchecked and continue through `/opsx-modify`',
        ]
        for path in self.root.glob('.agents/skills/*/SKILL.md'):
            original = path.read_text()
            for line in old_lines:
                with self.subTest(skill=path.parent.name, line=line):
                    path.write_text(original + '\n' + line + '\n')
                    self.assertTrue(validator.validate_apply_execution_contract(path))

    def test_missing_source_and_empty_section_are_rejected(self):
        original = self.doc.read_text()
        self.doc.unlink()
        self.assertTrue(validator.validate_apply_contract_source())
        self.doc.write_text(original.replace('### 中断续接', '### 已删除续接'))
        self.assertTrue(validator.validate_apply_contract_source())
        self.doc.write_text('## Apply 连续执行契约\n\n' + '\n'.join('### ' + h + '\n' for h in validator.APPLY_CONTRACT_SECTIONS))
        self.assertEqual(len(validator.validate_apply_contract_source()), 8)

    def test_missing_behavior_checker_and_decision_are_rejected(self):
        (self.root / "scripts/validate-apply-behavior.py").unlink()
        self.assertIn("缺少apply行为轨迹校验器", validator.validate_apply_contract_source())
        self.doc.write_text(self.doc.read_text().replace("### 停止前决策", "### 删除决策"))
        self.assertTrue(any("停止前决策" in e for e in validator.validate_apply_contract_source()))

    def test_explicit_prohibition_of_old_instruction_is_allowed(self):
        path = self.root / ".agents/skills/opsx-apply/SKILL.md"
        path.write_text(path.read_text() + "\nMUST NOT use: Pause on errors, blockers, or unclear requirements\n")
        self.assertEqual(validator.validate_apply_execution_contract(path), [])

    def test_unrelated_skill_is_outside_scope(self):
        path = self.root / '.agents/skills/explore/SKILL.md'
        self.assertEqual(validator.validate_apply_execution_contract(path), [])


if __name__ == '__main__':
    unittest.main()
