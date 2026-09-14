#!/usr/bin/env python3
"""校验脱敏apply决策轨迹；--self-test运行合成正反例，不代表真实Agent验收。"""
import argparse
import json
from pathlib import Path


class InvalidTrace(ValueError):
    pass


def expected_action(record):
    if not record.get('evidence'):
        raise InvalidTrace('缺少证据引用')
    trigger = record['trigger']
    if trigger not in {'work', 'test_failure', 'progress_question', 'compaction', 'user_stop', 'platform_stop'}:
        raise InvalidTrace('未知触发事件')
    if trigger in {'user_stop', 'platform_stop'}:
        return 'stop'
    tasks = record['tasks']
    if not tasks or len({t['id'] for t in tasks}) != len(tasks):
        raise InvalidTrace('任务为空或ID重复')
    by_id = {t['id']: t for t in tasks}
    visited, visiting = set(), set()

    def visit(key):
        if key not in by_id or key in visiting:
            raise InvalidTrace('缺失依赖或依赖成环')
        if key in visited:
            return
        visiting.add(key)
        t = by_id[key]
        if t['state'] not in {'pending', 'done'}:
            raise InvalidTrace('未知任务状态')
        for dep in t.get('deps', []):
            visit(dep)
        if t.get('external') and not t.get('blocker_evidence'):
            raise InvalidTrace('外部阻塞缺少证据')
        visiting.remove(key)
        visited.add(key)

    for key in by_id:
        visit(key)
    pending = [t for t in tasks if t['state'] != 'done']
    if not pending:
        return 'complete' if record.get('gates_passed') is True else 'continue'
    ready = [t for t in pending if not t.get('external') and all(by_id[d]['state'] == 'done' for d in t.get('deps', []))]
    return 'continue' if ready else 'wait'


def validate(data):
    if data.get('source') not in {'synthetic', 'observed'} or not data.get('records'):
        raise InvalidTrace('缺少来源或轨迹')
    errors = []
    for i, record in enumerate(data['records']):
        expected = expected_action(record)
        if record.get('action') != expected:
            errors.append(f'记录{i + 1}: 应为{expected}，实际为{record.get("action")}')
    return errors


def self_test():
    cases = []
    def add(name, trigger='work', tasks=None, gates=False, expected='continue'):
        cases.append((name, dict(trigger=trigger, tasks=tasks or [dict(id='repair',state='pending')], gates_passed=gates, evidence=['fixture'], action=expected)))
    add('测试失败自修', 'test_failure')
    add('进度插话续做', 'progress_question')
    add('压缩后续做', 'compaction')
    blocked = dict(id='deploy', state='pending', external='login', blocker_evidence=['fixture-login'])
    add('部署缺配置仍开发', tasks=[blocked, dict(id='test', state='pending')])
    add('等待登录', tasks=[blocked], expected='wait')
    add('传递依赖等待', tasks=[blocked, dict(id='verify',state='pending',deps=['deploy'])], expected='wait')
    add('用户停止', 'user_stop', expected='stop')
    add('平台终止', 'platform_stop', expected='stop')
    add('完整完成', tasks=[dict(id='test',state='done')], gates=True, expected='complete')
    add('遗漏完成门禁', tasks=[dict(id='test',state='done')])
    count = 0
    for name, record in cases:
        assert not validate(dict(source='synthetic',records=[record])), name
        count += 1
        for wrong in {'continue','wait','stop','complete'} - {record['action']}:
            assert validate(dict(source='synthetic',records=[dict(record,action=wrong)])), name
            count += 1
    malformed = [[], [dict(id='a',state='pending',deps=['missing'])], [dict(id='a',state='pending',deps=['a'])], [dict(id='a',state='pending',external='login')]]
    for tasks in malformed:
        try:
            expected_action(dict(trigger='work',tasks=tasks,evidence=['fixture']))
        except InvalidTrace:
            count += 1
        else:
            raise AssertionError('未拒绝非法依赖')
    print(json.dumps(dict(source='synthetic', passed=count, scenarios=len(cases)),ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--self-test',action='store_true')
    group.add_argument('--trace',type=Path,help='脱敏JSON轨迹，格式见docs/standards/apply-behavior-acceptance.md')
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    try:
        data = json.loads(args.trace.read_text())
        errors = validate(data)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print('轨迹无效：'+type(exc).__name__)
        return 1
    print(json.dumps(dict(source=data['source'], records=len(data['records']), errors=errors),ensure_ascii=False))
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
