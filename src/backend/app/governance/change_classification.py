"""Pure classification contract shared by document creation and card projection."""
from datetime import datetime

PRIORITIES = ('P0', 'P1', 'P2', 'P3')
SEVERITIES = ('blocker', 'critical', 'high', 'medium', 'low')


def classification(change_id, metadata):
    inferred = 'fix' if change_id.startswith('fix-') else 'non_fix'
    declared = metadata.get('change_type')
    kind = declared if declared in ('fix', 'non_fix') else inferred
    conflict = declared is not None and (declared not in ('fix', 'non_fix') or declared != inferred)
    dimension = 'severity' if kind == 'fix' else 'priority'
    value = metadata.get(dimension)
    levels = SEVERITIES if kind == 'fix' else PRIORITIES
    state = 'invalid' if conflict else 'missing' if value is None else 'valid' if value in levels else 'invalid'
    assessment = metadata.get('classification')
    if assessment is not None:
        if not isinstance(assessment, dict) or assessment.get('dimension') != dimension or assessment.get('state') not in ('pending', 'assessed'):
            state = 'invalid'
        elif assessment['state'] == 'pending' and state != 'invalid':
            state = 'missing'
    return {'classification_dimension': dimension, 'classification_state': state,
            'priority': value if dimension == 'priority' and state == 'valid' else '',
            'severity': value if dimension == 'severity' and state == 'valid' else ''}


def validate_assessment(change_id, metadata):
    """Do not manufacture a grade: the creating agent supplies evidence and judgment."""
    result = classification(change_id, metadata)
    if metadata.get('change_type') not in ('fix', 'non_fix') or result['classification_state'] != 'valid':
        raise ValueError('独立 Change 类型或分级待评估/待核实，创建尚未完成')
    record = metadata.get('classification')
    if not isinstance(record, dict) or record.get('state') != 'assessed':
        raise ValueError('独立 Change 缺少已完成评估记录')
    for field in ('rationale', 'evaluated_by'):
        if not isinstance(record.get(field), str) or not record[field].strip():
            raise ValueError('独立 Change 评估缺少理由、主体或时间')
    try:
        timestamp = record.get('evaluated_at')
        if not isinstance(timestamp, datetime):
            if not isinstance(timestamp, str):
                raise ValueError('missing timestamp')
            datetime.fromisoformat(timestamp)
    except ValueError as exc:
        raise ValueError('独立 Change 评估时间无效') from exc
    refs = record.get('evidence_refs')
    if not isinstance(refs, list) or not refs or any(not isinstance(ref, str) or not ref.strip() for ref in refs):
        raise ValueError('独立 Change 评估缺少证据引用')
    return result
