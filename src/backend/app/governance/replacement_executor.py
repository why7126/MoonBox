"""Trusted archive driver. Runtime tools are deployed read-only, outside Agent writes.

This driver is deliberately unavailable on an ordinary writable source checkout.
The controller owns the project lock and authorization fence for its whole call.
"""
from pathlib import Path
import os
import re
import shutil
import subprocess
import sys
import tempfile
from .archive_recovery import tree_hash, verify_delta_effects, archive_paths


class ArchiveDriver:
    def __init__(self, project):
        self.project=project
        entry=shutil.which('openspec')
        if not entry: raise ValueError('archive_tool_unavailable')
        self.openspec=Path(entry).resolve()
        self.scripts=project.root/'scripts'
        self._trusted(self.openspec.parent.parent)
        self._trusted(self.scripts)
        self.tool_hash=tree_hash(self.openspec.parent.parent)
        self.script_hash=tree_hash(self.scripts)

    @staticmethod
    def _trusted(path):
        if not path.exists() or path.is_symlink() or any(os.access(p,os.W_OK) for p in (path,*path.parents)):
            raise ValueError('archive_tools_not_trusted')
        if path.is_dir() and any(p.is_symlink() or os.access(p,os.W_OK) for p in path.rglob('*')):
            raise ValueError('archive_tools_not_trusted')

    def recheck_tools(self):
        self._trusted(self.openspec.parent.parent);self._trusted(self.scripts)
        if tree_hash(self.openspec.parent.parent)!=self.tool_hash or tree_hash(self.scripts)!=self.script_hash:
            raise ValueError('archive_tool_changed')

    def _run(self,args,root):
        self.recheck_tools()
        from .controlled_successor import _authority
        from .replacement_proof import canonical
        from .replacement_tool_context import SCRIPTS
        context = _authority.get()
        read_fd = None
        if context and args[0] == sys.executable and Path(args[1]).name in SCRIPTS:
            _, project, actor, operation_id, fence = context
            if project.key != self.project.key or Path(root) != project.root:
                raise ValueError('tool_project_changed')
            read_fd, write_fd = os.pipe()
            try:
                os.write(write_fd, canonical({'actor': actor, 'space_id': project.space_id,
                    'repository_id': project.repository_id, 'binding_revision': project.binding_revision,
                    'operation_id': operation_id, 'fence': fence}))
            finally:
                os.close(write_fd)
            args = [sys.executable, '-m', 'app.governance.replacement_tool_context',
                    str(read_fd), Path(args[1]).name, *args[2:]]
        try:
            result=subprocess.run(args,cwd=root,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=180,
                pass_fds=() if read_fd is None else (read_fd,))
        except subprocess.TimeoutExpired:
            raise ValueError('archive_tool_timeout') from None
        finally:
            if read_fd is not None: os.close(read_fd)
        self.recheck_tools()
        output=result.stdout+'\n'+result.stderr
        if result.returncode or re.search(r'(?im)^(?:Aborted\.|.*(?:MODIFIED|ADDED|REMOVED|RENAMED) failed\b|Error:)',output):
            raise ValueError('archive_tool_failed')

    def preview(self,change):
        root=self.project.root
        before=tree_hash(root/'openspec/specs')
        with tempfile.TemporaryDirectory(prefix='moonbox-controlled-preview-') as tmp:
            target=Path(tmp);(target/'openspec/changes').mkdir(parents=True)
            shutil.copytree(root/'openspec/specs',target/'openspec/specs')
            shutil.copytree(root/'openspec/changes'/change,target/'openspec/changes'/change)
            for name in ('config.yaml','project.md'):
                if (root/'openspec'/name).exists():shutil.copy2(root/'openspec'/name,target/'openspec'/name)
            self._run([str(self.openspec),'archive',change,'-y'],target)
            candidates=[p for base in ('openspec/archive','openspec/changes/archive') for p in (target/base).glob(f'????-??-??-{change}') if p.is_dir()]
            if len(candidates)!=1 or (target/'openspec/changes'/change).exists():raise ValueError('archive_preview_ambiguous')
            verify_delta_effects(candidates[0]/'specs',target/'openspec/specs')
            expected=tree_hash(target/'openspec/specs')
        if tree_hash(root/'openspec/specs')!=before:raise ValueError('archive_inputs_changed')
        return expected

    def prepare(self,change):
        import importlib.util
        from datetime import datetime, timezone
        self.recheck_tools()
        spec=importlib.util.spec_from_file_location('controlled_archive_guard',self.scripts/'archive-recovery-guard.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        module.classify(self.project.root,change,datetime.now(timezone.utc).date().isoformat())
        from .archive_recovery import read_record,journal_path
        return read_record(journal_path(self.project.root,change))['expected_spec_hash']

    def validate_static(self,change):
        for script,args in (
            ('validate-change-delivery-evidence.py',['--change',change]),
            ('validate-change-identity.py',[]),
            ('validate-directory-structure.py',[]),
            ('validate-openspec-language.py',[]),
            ('validate-env-ignore-policy.py',[]),
        ):
            self._run([sys.executable,str(self.scripts/script),*args],self.project.root)

    def merge_and_move(self,change,*,move_only=False):
        self._run([str(self.openspec),'archive',change,'-y',*(['--skip-specs'] if move_only else [])],self.project.root)
        # Only this operation's unique legacy output is eligible for relocation.
        root=self.project.root
        legacy=list((root/'openspec/changes/archive').glob(f'????-??-??-{change}'))
        if legacy:
            canonical=list((root/'openspec/archive').glob(f'????-??-??-{change}'))
            if len(legacy)!=1 or canonical:raise ValueError('archive_identity_ambiguous')
            target=root/'openspec/archive'/legacy[0].name
            target.parent.mkdir(exist_ok=True,parents=True)
            os.rename(legacy[0],target)
            if not any((root/'openspec/changes/archive').iterdir()):(root/'openspec/changes/archive').rmdir()

    def finalize(self,change):
        # These scripts are deployed read-only; no repository-defined shell code.
        for script,args in (
            ('sync-workflow-status.py',['--event','opsx.archive','--change',change,'--sprint','auto']),
            ('promote-issues-for-archive.py',['--change',change,'--reason','controlled-archive']),
        ):
            self._run([sys.executable,str(self.scripts/script),*args],self.project.root)
