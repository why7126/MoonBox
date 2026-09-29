"""Validate focused generated artifacts before any workflow projection writes."""
import importlib.util
from pathlib import Path

module_path = Path(__file__).resolve().parents[2] / 'src/backend/app/governance/titles.py'
spec = importlib.util.spec_from_file_location('governance_titles_gate', module_path)
titles = importlib.util.module_from_spec(spec)
spec.loader.exec_module(titles)


def validate_generated(root, event, issue_id=None, change_id=None):
    if not event or event.split('.')[-1] not in {'capture','generate','complete','review','opsx'}:
        return []
    files=[]
    if event.endswith('.opsx') and change_id:
        directory = root/'openspec/changes'/change_id
        files=sorted(set(directory.rglob('*.md')) | {directory/name for name in ('proposal.md', 'design.md', 'tasks.md', 'trace.md')})
    elif event.endswith('.opsx'):
        return ['标题门禁：缺少 Change 身份']
    elif issue_id:
        folder='bugs' if issue_id.startswith('BUG-') else 'requirements'
        dirs=list((root/'issues'/folder).glob('*/'+issue_id))
        if len(dirs)!=1:
            return ['标题门禁：Issue身份缺失或不唯一']
        names={'capture':['capture.md','trace.md'], 'generate':['bug.md' if folder=='bugs' else 'requirement.md','trace.md'],
               'complete':[], 'review':['review.md','trace.md']}[event.split('.')[-1]]
        files=[dirs[0]/n for n in names] if names else list(dirs[0].glob('*.md'))
    errors=[]
    for file in files:
        if not file.exists():
            errors.append(f'{file.name}: 生成文档缺失')
        else:
            errors.extend(f'{file.name}: {e}' for e in titles.validate_document(file.read_text()))
    return errors
