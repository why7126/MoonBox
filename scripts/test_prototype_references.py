"""Isolated regression for prototype migration safety; no real Issue moves."""
from pathlib import Path
import runpy
import sys
from types import SimpleNamespace
from unittest.mock import patch
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from workflow_sync.prototype_references import check_references

ROOT = Path(__file__).resolve().parents[1]


class PrototypeReferencesTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.src = self.root / 'issues/requirements/plan/REQ-0099-test'
        self.dst = self.root / 'issues/requirements/review/REQ-0099-test'
        self.write('trace.md', '---\nlifecycle_stage: plan\n---\n# 追溯\n')
        self.write('prototype/web/index.html', '<link href="style.css"><img src="image%20one.svg?v=1#x">')
        self.write('prototype/web/style.css', 'body {background:url("image one.svg")}')
        self.write('prototype/web/image one.svg', '<svg/>')
        self.write('requirement.md', '[原型](prototype/web/index.html)\n')
        self.ns = runpy.run_path(str(ROOT / 'scripts/promote-issue-stage.py'))

    def write(self, name, text):
        p = self.src / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        return p

    def findings(self, changes=None):
        return check_references(self.root, self.src, self.dst, changes)

    def snapshot(self):
        return {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}

    def promote(self, dry=False):
        issue = self.ns['candidate_from_dir']('req', self.src)
        before = issue.trace_path.read_text()
        promotion = self.ns['Promotion'](issue, self.dst, before, before.replace('plan','review'), 'test')
        report = self.ns['Report']()
        code = self.ns['apply_promotions'](self.root, [promotion], SimpleNamespace(check=False, dry_run=dry), report)
        return code, report

    def test_normal_resources_and_preview_are_readonly(self):
        before = self.snapshot()
        self.assertEqual([], self.findings())
        self.assertEqual(0, self.promote(True)[0])
        self.assertEqual(before, self.snapshot())
        self.assertFalse(self.dst.exists())
        self.assertEqual(0, self.promote()[0])
        self.assertEqual([], check_references(self.root, self.dst, self.dst))

    def test_old_stage_link_blocks_before_any_write(self):
        self.write('requirement.md', f'[原型]({self.src.relative_to(self.root)}/prototype/web/index.html)')
        before = self.snapshot()
        for dry in (True, False):
            code, report = self.promote(dry)
            self.assertEqual(1, code)
            self.assertTrue(any('migration-break' in x for x in report.blocked))
            self.assertEqual(before, self.snapshot())

    def test_existing_missing_resource(self):
        (self.src/'prototype/web/image one.svg').unlink()
        self.assertTrue(any(f.reason == 'existing-missing' and f.blocking for f in self.findings()))

    def test_history_fences_and_active_section(self):
        self.write('acceptance.md', '## 变更记录\n[旧](prototype/missing.html)\n### 旧轮次\nprototype/old.html\n'
                   '## 当前验收\n```md\nprototype/example.html\n```\n[当前](prototype/web/index.html)\n')
        findings = self.findings()
        self.assertFalse(any(f.blocking for f in findings))
        self.assertEqual({'history','example'}, {f.reason for f in findings})
        self.write('acceptance.md', '## 当前验收\n[旧路径](prototype/missing.html)')
        self.assertTrue(any(f.blocking for f in self.findings()))

    def test_reference_links_and_future_target(self):
        self.write('requirement.md', f'[原型][ui]\n[ui]: {self.dst.relative_to(self.root)}/prototype/web/index.html\n')
        self.assertFalse(any(f.blocking for f in self.findings()))

    def test_related_change_and_sprint_inbound_links(self):
        directory = self.root/'openspec/changes/test-change'
        directory.mkdir(parents=True)
        (directory/'design.md').write_text(f'[原型]({self.src.relative_to(self.root)}/prototype/web/index.html)')
        sprint = self.root/'iterations/change/sprint-001'
        sprint.mkdir(parents=True)
        (sprint/'sprint.yaml').write_text(f'requirements:\n  - {self.src.name}\n')
        (sprint/'sprint.md').write_text(f'[原型]({self.src.relative_to(self.root)}/prototype/web/index.html)')
        findings = self.findings(['test-change'])
        self.assertEqual(2, sum(f.blocking for f in findings))

    def test_remote_dynamic_root_relative_and_anchor_are_not_missing(self):
        self.write('prototype/web/index.html', '<script src="https://example.invalid/a.js?token=secret"></script>'
                   '<img src="${image}"><img src="/images/a.png"><a href="#ok">跳转</a>')
        findings = self.findings()
        self.assertFalse(any(f.blocking for f in findings))
        self.assertEqual({'external-skipped','dynamic-skipped','root-relative-unresolved'}, {f.reason for f in findings})
        self.assertNotIn('secret', str(findings))

    def test_css_import_srcset_inline_style_and_cycles(self):
        self.write('prototype/web/index.html', '<img srcset="image%20one.svg 1x, missing.svg 2x">'
                   '<style>body{background:url(missing2.svg)}</style>')
        self.write('prototype/web/style.css', '@import "other.css";')
        self.write('prototype/web/other.css', '@import "style.css";')
        findings = self.findings()
        self.assertEqual(2, sum(f.blocking for f in findings))

    def test_symlink_and_escape_are_rejected(self):
        self.write('prototype/web/index.html','<img src="linked.svg">')
        (self.src/'prototype/web/linked.svg').symlink_to('/etc/passwd')
        findings = self.findings()
        self.assertTrue(any(f.reason=='unsafe-path' and f.blocking for f in findings))
        self.assertNotIn('/etc/passwd', str(findings))

    def test_no_prototype_or_references_is_allowed(self):
        import shutil
        shutil.rmtree(self.src/'prototype')
        self.write('requirement.md','# 无原型\n')
        self.assertEqual([], self.findings())

    def test_postcheck_failure_is_not_success_and_retry_verifies(self):
        import shutil
        real_move = shutil.move
        def move_then_remove(src, dst):
            real_move(src, dst)
            (Path(dst)/'prototype/web/image one.svg').unlink()
        with patch('shutil.move', side_effect=move_then_remove):
            code, report = self.promote()
        self.assertEqual(1, code)
        self.assertEqual([], report.promoted)
        self.assertTrue(self.dst.is_dir())
        moved = self.ns['candidate_from_dir']('req', self.dst)
        self.assertFalse(self.ns['reference_gate'](self.root,moved,self.dst,self.ns['Report']()))
        (self.dst/'prototype/web/image one.svg').write_text('<svg/>')
        self.assertTrue(self.ns['reference_gate'](self.root,moved,self.dst,self.ns['Report']()))

    def test_check_mode_and_cli_retry_are_readonly(self):
        before = self.snapshot()
        with patch.object(sys, 'argv', ['promote-issue-stage.py', '--req', self.src.name, '--to', 'review', '--check']), patch('pathlib.Path.cwd', return_value=self.root):
            (self.root/'openspec').mkdir()
            self.assertEqual(1, self.ns['main']())
        self.assertEqual(before, self.snapshot())
        self.promote()
        (self.dst/'prototype/web/image one.svg').unlink()
        with patch.object(sys, 'argv', ['promote-issue-stage.py', '--req', self.src.name, '--to', 'review', '--dry-run']), patch('pathlib.Path.cwd', return_value=self.root):
            self.assertEqual(1, self.ns['main']())

    def test_batch_blocker_does_not_prevent_independent_move(self):
        import shutil
        other = self.src.with_name('REQ-0100-test')
        shutil.copytree(self.src, other)
        self.write('requirement.md', '[坏链接](prototype/missing.html)')
        promotions = []
        for src in (self.src, other):
            issue = self.ns['candidate_from_dir']('req', src)
            before = issue.trace_path.read_text()
            promotions.append(self.ns['Promotion'](issue,self.dst.with_name(src.name),before,before,'test'))
        report = self.ns['Report']()
        code = self.ns['apply_promotions'](self.root,promotions,SimpleNamespace(check=False,dry_run=False),report)
        self.assertEqual(1,code)
        self.assertTrue(self.src.exists())
        self.assertTrue(self.dst.with_name(other.name).exists())
        self.assertEqual(1,len(report.promoted))

    def test_external_css_dependencies_are_followed(self):
        shared = self.root/'shared'
        shared.mkdir()
        (shared/'style.css').write_text('body{background:url(missing.png)}')
        self.write('prototype/web/index.html','<link href="../../../../../../shared/style.css">')
        self.assertTrue(any(f.file == 'shared/style.css' and f.blocking for f in self.findings()))

    def test_base_and_plain_remote_reference_are_not_false_missing(self):
        self.write('prototype/web/index.html','<base href="https://example.invalid/"><img src="remote.png">')
        self.write('requirement.md','原型 https://example.invalid/prototype/demo.html')
        findings = self.findings()
        self.assertFalse(any(f.blocking for f in findings))
        self.assertIn('unsupported-base', {f.reason for f in findings})

    def test_wrapper_preflight_excludes_blocked_issue_before_reconcile(self):
        ns = runpy.run_path(str(ROOT/'scripts/promote-issues-for-archive.py'))
        issue = SimpleNamespace(path=self.src)
        item = ns['PromotionCandidate'](self.src.name,'req','review','done',[],[],'test')
        self.write('requirement.md','[坏链接](prototype/missing.html)')
        main = ns['main']
        with patch.dict(main.__globals__, ROOT=self.root,
                        load_all_issues=lambda: {self.src.name: issue},
                        collect_candidates_for_change=lambda *args: [item],
                        issues_linked_to_change=lambda *args: [],
                        reconcile_safe_residuals=lambda candidates,*args,**kwargs: self.assertEqual([],candidates) or {},
                        print_reconcile_results=lambda *args: None,
                        collect_residual_blockers=lambda *args: [],
                        run_promotions=lambda *args,**kwargs: 0,
                        refresh_promoted_indexes=lambda *args,**kwargs: 0), patch.object(sys,'argv',['promote','--change','test']):
            before=self.snapshot()
            self.assertEqual(1,main())
            self.assertEqual(before,self.snapshot())

    def test_prototype_named_html_in_structured_refs_is_not_truncated(self):
        self.write('prototype/web/prototype.html','<p>原型</p>')
        self.write('trace.md', 'prototype_refs:\n- path: '+str(self.dst.relative_to(self.root))+'/prototype/web/prototype.html\n')
        self.assertEqual([], self.findings())

    def test_postcheck_detects_external_old_stage_link(self):
        directory=self.root/'openspec/changes/test-change'
        directory.mkdir(parents=True)
        (directory/'design.md').write_text('[原型]('+str(self.src.relative_to(self.root))+'/prototype/web/index.html)')
        import shutil
        self.dst.parent.mkdir(parents=True)
        shutil.move(self.src,self.dst)
        findings=check_references(self.root,self.dst,self.dst,['test-change'])
        self.assertTrue(any(f.blocking and f.file.endswith('design.md') for f in findings))

    def test_wrapper_retry_rechecks_already_archived_directory(self):
        import shutil
        target=self.root/'issues/requirements/archive'/self.src.name
        target.parent.mkdir(parents=True)
        shutil.move(self.src,target)
        (target/'prototype/web/image one.svg').unlink()
        ns=runpy.run_path(str(ROOT/'scripts/promote-issues-for-archive.py'))
        issue=SimpleNamespace(path=target,issue_id=target.name,kind='req',openspec_changes=[],related_changes=[])
        main=ns['main']
        with patch.dict(main.__globals__, ROOT=self.root,
                        load_all_issues=lambda: {target.name:issue},
                        collect_candidates_for_change=lambda *args: [],
                        issues_linked_to_change=lambda *args: [issue],
                        reconcile_safe_residuals=lambda *args,**kwargs: {},
                        print_reconcile_results=lambda *args: None,
                        collect_residual_blockers=lambda *args: [],
                        run_promotions=lambda *args,**kwargs: 0,
                        refresh_promoted_indexes=lambda *args,**kwargs: 0), patch.object(sys,'argv',['promote','--change','test']):
            self.assertEqual(1,main())


if __name__ == '__main__':
    unittest.main()
