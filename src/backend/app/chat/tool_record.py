"""Bounded, allowlisted tool details for the existing private conversation event stream."""
import math
import re
import time


def display_text(value, workspace, limit=6000):
    text = str(value).replace(str(workspace), '[工作区]')
    text = re.sub(r'-----BEGIN [^-]*PRIVATE KEY-----[\s\S]*?(?:-----END [^-]*PRIVATE KEY-----|$)', '[已脱敏]', text)
    text = re.sub(r'\b(?:sk-[\w-]{12,}|eyJ[\w-]+\.[\w-]+\.[\w-]+)\b', '[已脱敏]', text)
    text = re.sub(r'(?i)(bearer\s+)\S+', r'\1[已脱敏]', text)
    text = re.sub(r'''(?ix)(["']?(?:authorization|cookie|api[_-]?key|password|secret|access[_-]?token|token)["']?\s*[:=]\s*)(?:"[^"\n]*"|'[^'\n]*'|[^\s,;]+)''', r'\1[已脱敏]', text)
    text = re.sub(r'(?i)(--(?:password|token|api-key|secret)\s+)(?:"[^"\n]*"|\S+)', r'\1[已脱敏]', text)
    text = re.sub(r'(?:/Users/|/home/)[^\s"\'<>]+', '[本机路径]', text)
    text = re.sub(r'([a-zA-Z][a-zA-Z0-9+.-]*://)[^\s/@]+:[^\s/@]+@', r'\1[已脱敏]@', text)
    return text[:limit], len(text) > limit


def tool_payload(item, phase, executor_turn, workspace, started, *, clock=time.monotonic):
    """No raw event/config/schema capture. Missing fields remain unavailable."""
    key = item['id']; now = clock()
    if phase == 'started': started.setdefault(key, now)
    result = dict(item_id=key, executor_turn_id=executor_turn, type=item['type'], phase=phase,
                  detail_version=1, recorded_at_ms=int(time.time()*1000), timing_source='worker_observed', truncated=False)
    def clean(value, limit=6000):
        text, truncated = display_text(value, workspace, limit)
        result['truncated'] |= truncated
        return text
    if item['type'] == 'commandExecution':
        result['tool_name'] = '命令执行'
        result['arguments'] = {k: clean(item[k]) for k in ('command', 'cwd') if isinstance(item.get(k), str)}
        if isinstance(item.get('aggregatedOutput'), str): result['result'] = clean(item['aggregatedOutput'])
        if type(item.get('exitCode')) is int: result['exit_code'] = item['exitCode']
    else:
        result['tool_name'] = '文件变更'
        changes = item.get('changes')
        if isinstance(changes, list):
            result['arguments'] = {'files': [clean(c['path'], 240) for c in changes[:20] if isinstance(c, dict) and isinstance(c.get('path'), str)]}
            result['truncated'] |= len(changes) > 20
    status = item.get('status')
    if status in ('inProgress', 'completed', 'failed', 'declined'): result['status'] = status
    if phase == 'completed':
        duration = item.get('durationMs')
        if type(duration) in (int, float) and math.isfinite(duration) and duration >= 0:
            result['duration_ms'] = duration; result['timing_source'] = 'executor'
        elif key in started: result['duration_ms'] = max(0, round((now-started[key])*1000))
        started.pop(key, None)
    return result
