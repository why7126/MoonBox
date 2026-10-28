"""探索维护契约负向回归；不调用模型，不代表行为质量评测。"""
import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('context_validator', ROOT / 'scripts/validate-agent-context-budget.py')
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)
FILES = (
    '.agents/skills/explore/SKILL.md',
    'docs/standards/governance-feedback-loop.md',
    '.agents/skills/spec-opt/SKILL.md',
    'AGENTS.md',
    'rules/agent-context-budget.md',
    '.agents/skills/explore/evals/cases.md',
)


class ExploreFeedbackContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in FILES:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)

    def test_current_contract(self):
        self.assertEqual([], validator.validate_explore_feedback_contract(self.root))

    def test_missing_files_are_reported(self):
        for name in FILES:
            with self.subTest(name=name):
                path = self.root / name
                content = path.read_text()
                path.unlink()
                self.assertTrue(any(name in e for e in validator.validate_explore_feedback_contract(self.root)))
                path.write_text(content)

    def test_boundary_and_classification_regressions(self):
        mutations = {
            FILES[0]: ['只读不落盘', '项目事实', '局部偏好', '执行遗漏', '环境问题',
                       '通用方法缺陷', '重复问题合并候选', '当前任务固定版本',
                       '新任务重新读取', '未运行旧版/候选版对照', '无问题不制造候选'],
            FILES[1]: ['不扩展 CLI schema', 'plan/decide', '一票否决', '回退仅撤回本次差异'],
            FILES[2]: ['候选去重', '版本生效'],
            FILES[5]: ['E09', 'E10', '硬失败', '未执行'],
        }
        for name, terms in mutations.items():
            path = self.root / name
            original = path.read_text()
            for term in terms:
                with self.subTest(name=name, term=term):
                    path.write_text(original.replace(term, '删除后的占位内容'))
                    self.assertTrue(any(term in e for e in validator.validate_explore_feedback_contract(self.root)))
                    path.write_text(original)

    def test_unrelated_prose_does_not_fail(self):
        path = self.root / FILES[0]
        path.write_text(path.read_text() + '\n与试点无关的说明。\n')
        self.assertEqual([], validator.validate_explore_feedback_contract(self.root))


if __name__ == '__main__':
    unittest.main()
