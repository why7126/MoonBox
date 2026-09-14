"""服务端仓库目录：只返回显式配置的非路径标识。"""
import json
import os
import re


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
