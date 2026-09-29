"""服务端仓库目录：只返回显式配置的非路径标识。"""
import json
import os
import re
import subprocess
from pathlib import Path


def backup_root():
    """仅运维显式配置本地备份库；空值维持未接入状态。"""
    return os.environ.get('MOONBOX_CHAT_BACKUP_ROOT', '').strip() or None


def repository_catalog():
    try:
        entries = json.loads(os.environ.get('MOONBOX_CHAT_REPOSITORIES', '[]'))
        if not isinstance(entries, list) or len(entries) > 100:
            return []
        result = []
        for entry in entries:
            if not isinstance(entry, dict):
                return []
            if any(not isinstance(entry.get(k), str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', entry[k]) for k in ('id','space_id')):
                return []
            result.append({'id': entry['id'], 'space_id': entry['space_id']})
        return result
    except (ValueError, TypeError):
        return []


def execution_limits():
    """Explicit unlimited is distinct from missing configuration; bytes bound processing."""
    keys = ('user_concurrency', 'space_concurrency', 'user_monthly_tokens', 'space_monthly_tokens',
            'user_storage_bytes', 'space_storage_bytes', 'turn_reserved_tokens', 'turn_reserved_bytes')
    try:
        value = json.loads(os.environ.get('MOONBOX_CHAT_LIMITS', '{}'))
        if not isinstance(value, dict): return None
        result = {}
        for key in keys:
            item = value.get(key)
            if item == 'unlimited' and key != 'turn_reserved_bytes':
                result[key] = None
            elif type(item) is int and 0 < item <= 10**15:
                result[key] = item
            else: return None
        for resource, reservation in (('monthly_tokens','turn_reserved_tokens'),('storage_bytes','turn_reserved_bytes')):
            for kind in ('user','space'):
                cap = result[f'{kind}_{resource}']; amount = result[reservation]
                if cap is not None and (amount is None or amount > cap): return None
        return result
    except (ValueError, TypeError):
        return None


def execution_config():
    """Server-owned execution choices; values are stable identifiers, never credentials."""
    default = {
        'policy_version': 'chat-execution-config-v1',
        'agents': [{'value': 'codex', 'display_name': 'Codex', 'available': True, 'disabled_reason': None}],
        'models': [
            {'value': 'gpt-6-astra', 'display_name': 'GPT-6 Astra', 'available': True, 'disabled_reason': None},
            {'value': 'gpt-5.6-sol', 'display_name': 'GPT-5.6 Sol', 'available': True, 'disabled_reason': None},
            {'value': 'gpt-5.6-terra', 'display_name': 'GPT-5.6 Terra', 'available': True, 'disabled_reason': None},
            {'value': 'gpt-5.6-luna', 'display_name': 'GPT-5.6 Luna', 'available': True, 'disabled_reason': None},
            {'value': 'gpt-5.5', 'display_name': 'GPT-5.5', 'available': True, 'disabled_reason': None},
        ],
        'reasoning': [
            {'value': 'low', 'display_name': 'Low', 'available': True, 'disabled_reason': None},
            {'value': 'medium', 'display_name': 'Medium', 'available': True, 'disabled_reason': None},
            {'value': 'high', 'display_name': 'High', 'available': True, 'disabled_reason': None},
            {'value': 'xhigh', 'display_name': 'XHigh', 'available': True, 'disabled_reason': None},
        ],
        'defaults': {'agent': 'codex', 'model': 'gpt-6-astra', 'reasoning': 'high'},
    }
    try:
        configured = json.loads(os.environ.get('MOONBOX_CHAT_EXECUTION_CONFIG', '{}'))
        if not isinstance(configured, dict):
            return default
        candidate = {**default, **configured}
        for group in ('agents', 'models', 'reasoning'):
            if not _valid_options(candidate.get(group)):
                return default
        defaults = candidate.get('defaults')
        if not isinstance(defaults, dict) or not all(isinstance(defaults.get(k), str) for k in ('agent', 'model', 'reasoning')):
            return default
        if any(defaults[key] not in {item['value'] for item in candidate[group]} for key, group in (('agent', 'agents'), ('model', 'models'), ('reasoning', 'reasoning'))):
            return default
        policy = candidate.get('policy_version')
        candidate['policy_version'] = policy if isinstance(policy, str) and re.fullmatch(r'[A-Za-z0-9_.:-]{1,64}', policy) else default['policy_version']
        return candidate
    except (ValueError, TypeError):
        return default


def _valid_options(value):
    if not isinstance(value, list) or not 1 <= len(value) <= 50:
        return False
    seen = set()
    for item in value:
        if not isinstance(item, dict):
            return False
        option = item.get('value')
        name = item.get('display_name')
        available = item.get('available')
        reason = item.get('disabled_reason')
        if not isinstance(option, str) or not re.fullmatch(r'[A-Za-z0-9_.:-]{1,80}', option) or option in seen:
            return False
        if not isinstance(name, str) or not 1 <= len(name) <= 120:
            return False
        if type(available) is not bool:
            return False
        if reason is not None and (not isinstance(reason, str) or len(reason) > 160):
            return False
        seen.add(option)
    return True


def repository_binding(repository_id, space_id):
    """Private paths are separate from the public opaque repository catalog."""
    if not any(row['id'] == repository_id and row['space_id'] == space_id for row in repository_catalog()): return None
    try:
        rows = json.loads(os.environ.get('MOONBOX_CHAT_REPOSITORY_BINDINGS', '[]'))
        if not isinstance(rows, list): return None
        matches = [row for row in rows if isinstance(row, dict) and row.get('id') == repository_id and row.get('space_id') == space_id]
        if len(matches) != 1 or not isinstance(matches[0].get('governance_root'), str): return None
        return matches[0]
    except (ValueError, TypeError): return None


def repository_branches(repository_id, space_id):
    """Return sanitized branch choices from the bound repository; paths never leave the server."""
    binding = repository_binding(repository_id, space_id) or {}
    root = binding.get('source_root') or binding.get('governance_root')
    if not isinstance(root, str) or not root:
        return {'items': [{'name': 'main', 'is_default': True}], 'default': 'main', 'source': 'fallback'}
    repo = Path(root).resolve()
    if not (repo / '.git').exists():
        return {'items': [{'name': 'main', 'is_default': True}], 'default': 'main', 'source': 'fallback'}
    env = {'PATH': os.environ.get('PATH', '/usr/bin:/bin'), 'HOME': '/nonexistent',
           'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_GLOBAL': '/dev/null'}
    try:
        raw = subprocess.check_output(['git', '-C', str(repo), 'for-each-ref', '--format=%(refname:short)', 'refs/heads'],
            env=env, stderr=subprocess.DEVNULL, timeout=5).decode().splitlines()
        names = [name.strip() for name in raw if _valid_branch(name.strip())][:200]
        default = _default_branch(repo, env, names)
        if not names:
            names = [default]
        if 'main' in names:
            default = 'main'
        elif 'master' in names:
            default = 'master'
        items = [{'name': name, 'is_default': name == default} for name in names]
        return {'items': items, 'default': default, 'source': 'git'}
    except (subprocess.SubprocessError, OSError, UnicodeDecodeError):
        return {'items': [{'name': 'main', 'is_default': True}], 'default': 'main', 'source': 'fallback'}


def _valid_branch(name):
    return bool(name and len(name) <= 120 and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._/@+-]{0,119}', name)
        and '..' not in name and not name.endswith('.') and '@{' not in name and not name.startswith('/') and not name.endswith('/'))


def _default_branch(repo, env, names):
    try:
        value = subprocess.check_output(['git', '-C', str(repo), 'symbolic-ref', '--short', 'HEAD'],
            env=env, stderr=subprocess.DEVNULL, timeout=5).decode().strip()
        if value in names:
            return value
    except (subprocess.SubprocessError, OSError, UnicodeDecodeError):
        pass
    return 'main' if 'main' in names else 'master' if 'master' in names else names[0] if names else 'main'


def retention_limits():
    try:
        values=json.loads(os.environ.get('MOONBOX_CHAT_RETENTION','{}'))
        if not isinstance(values,dict):return None
        result = {}
        for key in ('executor_delete_seconds','backup_expiry_seconds'):
            item = values.get(key)
            if item == 'unlimited': result[key] = None
            elif type(item) is int and 1 <= item <= 365*86400: result[key] = item
            else: return None
        return result
    except (ValueError,TypeError):return None
