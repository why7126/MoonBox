"""Read-only Chat capability inventory; configuration is never test success."""
import json
import os
import time

from app.chat import service as chat
from app.chat.settings import repository_binding
from app.chat.workspace import trusted_directory, WorkspaceError
from app.verification.service import inspect_authorized
from app.verification.acceptance_template import approved_template
from app.verification.acceptance_state import Conflict


def inspect_conversation(db, actor, conversation_id):
    parent = chat.conversation(db, actor, conversation_id)
    binding = repository_binding(parent['repository_id'], parent['space_id'])
    if not binding:
        raise chat.ChatError(2503, '项目未绑定或不可访问', 403)
    browser = inspect_authorized(db, actor, parent['space_id'], parent['repository_id'])
    checks = []
    def add(name, status, reason=None):
        checks.append({'name': name, 'status': status, 'reason_code': reason})
    add('browser', browser['status'], browser['reason_code'])
    add('frontend', 'ready' if browser.get('checks', {}).get('dependencies') else 'unavailable',
        None if browser.get('checks', {}).get('dependencies') else 'project_dependencies_unverified')
    template_key = None
    try:
        template = approved_template(binding['source_root'])
        template_key = template.key
        add('python', 'configured', 'runtime_probe_required')
        add('isolated_acceptance', 'configured', 'runtime_probe_required')
    except (Conflict, OSError, KeyError):
        add('python', 'unavailable', 'acceptance_template_unavailable')
        add('isolated_acceptance', 'unavailable', 'acceptance_template_unavailable')
    try:
        root = trusted_directory(os.environ['MOONBOX_VERIFICATION_STATE_ROOT'])
        marker = root / 'worker-ready.json'
        if marker.is_symlink() or marker.stat().st_size > 4096:
            raise ValueError()
        heartbeat = json.loads(marker.read_text())
        alive = 0 <= time.time() - heartbeat['time'] < 5
        if (alive and browser['reason_code'] == 'verification_worker_unavailable'
                and heartbeat.get('image_digest') == os.getenv('MOONBOX_VERIFICATION_IMAGE_ID')
                and heartbeat.get('browser_reason') in {'browser_probe_failed', 'verification_toolchain_mismatch',
                    'browser_probe_cleanup_unconfirmed'}):
            checks[0]['reason_code'] = heartbeat['browser_reason']
        python = heartbeat.get('python', {})
        if (alive and template_key and python.get('template_key') == template_key
                and 0 <= time.time()-python.get('checked_at',0) < 90):
            for check in checks:
                if check['name']=='python':
                    if python.get('status') == 'ready':
                        check.update(status='ready',reason_code=None)
                    elif python.get('status') == 'unavailable':
                        reason=python.get('reason_code')
                        check.update(status='unavailable',reason_code=reason if reason in {
                            'python_test_runtime_unavailable','python_probe_cleanup_unconfirmed',
                            'container_runtime_unavailable'} else 'python_test_runtime_unavailable')
    except (KeyError, OSError, ValueError, TypeError, AttributeError, WorkspaceError):
        alive = False
    add('worker', 'ready' if alive else 'unavailable', None if alive else 'verification_worker_unavailable')
    return {'conversation_id': conversation_id, 'checked_at': chat.now(),
            'environment_key': browser.get('environment_key'), 'template_key': template_key,
            'checks': checks, 'acceptance_passed': False,
            'status': 'unavailable' if any(c['status']=='unavailable' for c in checks) else 'configured'}


def prompt_summary(result, *, tool_available):
    """Only server-owned enums and hashes; never include target URL or template contents."""
    return ('\n验收能力预检（不是验收结果）：'+json.dumps(result,ensure_ascii=False)+
        ('\n需要验收时调用moonbox_acceptance；不要在执行器联网补装或索取个人凭证。' if tool_available else
         '\n本轮预检未确认原生验收工具已注册，以实际工具清单为准；不要假称已调用。保留相关验收阻塞，可独立任务继续。')+
        '\n浏览器和前端项目绑定检查属于既有验证通道；隔离验收模板属于独立通道，前者缺失不代表后者不可调用。'+
        '\nconfigured仅表示配置存在，必须由实际探针和对应测试证明通过；缺失能力只阻塞依赖项，不勾选未验证任务。')
