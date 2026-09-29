"""Business titles shared by governance readers and generated-document gates."""
import re
from pathlib import Path
import yaml

GENERIC = {'需求', '缺陷', '缺陷说明', '变更提案', '提案', '设计', '技术设计', '任务清单', '实施任务', '追溯', '变更追溯', '实施与验证记录', '修复追溯', '验收清单', '验收记录', '验证记录', '根因分析', '临时规避', '业务流程', '用户故事', '评审', '现象', '概述', '背景', '目标'}


def business_title(value):
    if not isinstance(value, str):
        return None
    value = value.strip()
    if not value or '\n' in value or '\r' in value or not re.search(r'[\u4e00-\u9fff]', value):
        return None
    reduced = re.sub(r'^(?:(?:REQ|BUG)-\d+(?:-[a-z0-9-]+)?|Change)\s*[:：-]?\s*', '', value, flags=re.I)
    if reduced in GENERIC or re.search(r'<[^>]+>|\{\{.*?\}\}|待填写|此处填写|替换为', value):
        return None
    return value


def parse(text):
    metadata = {}
    body = text
    if text.startswith('---\n'):
        pieces = text.split('---', 2)
        if len(pieces) == 3:
            metadata = yaml.safe_load(pieces[1]) or {}
            body = pieces[2]
    if not isinstance(metadata, dict):
        raise ValueError('标题元数据格式错误')
    # Ignore fenced code examples when selecting a document heading.
    headings = []
    fence = None
    for line in body.splitlines():
        marker = re.match(r'^\s*(`{3,}|~{3,})', line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence is None and line.startswith('# '):
            headings.append(line[2:].strip())
    return metadata, headings


def read_title(path: Path):
    try:
        metadata, headings = parse(path.read_text(encoding='utf-8'))
        # Only missing metadata permits legacy H1 fallback; invalid explicit titles do not.
        return business_title(metadata['title']) if 'title' in metadata else next((t for h in headings if (t := business_title(h))), None)
    except (OSError, UnicodeError, ValueError, yaml.YAMLError):
        return None


def validate_document(text):
    try:
        metadata, headings = parse(text)
    except (ValueError, yaml.YAMLError):
        return ['title: 元数据格式错误']
    errors = []
    title = business_title(metadata.get('title'))
    if not title:
        errors.append('title: 缺少有效中文业务标题')
    if len(headings) != 1 or headings[0] != title:
        errors.append('H1: 需要唯一且与 title 一致的中文一级标题')
    return errors


def project_title(stage, registry_title, issue_id, main_path, proposal_path=None):
    fallback = business_title(registry_title)
    warning = None
    if stage in {'ready-dev', 'development', 'acceptance', 'done'}:
        title = read_title(proposal_path) if proposal_path else None
        if title:
            return title, 'proposal.md', None
        warning = '缺少唯一有效的 Change 提案标题，已回退'
    if stage != 'capture':
        title = read_title(main_path) if main_path else None
        if title:
            return title, main_path.name, warning
        warning = '缺少有效主文档标题，已回退'
    return fallback or issue_id, '_registry.yaml' if fallback else 'id', warning or (None if fallback else '缺少有效注册表标题，已回退编号')
