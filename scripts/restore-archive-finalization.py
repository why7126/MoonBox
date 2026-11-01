#!/usr/bin/env python3
"""预检或追加证明绑定的归档收尾投影；不修改原文、规格或原恢复日志。"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src/backend'))
from app.governance.archive_closure_restoration import restore


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--change', required=True)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--apply', action='store_true', help='排他追加恢复记录；不覆盖已有记录')
    parser.add_argument('--original-trace', type=Path, help='原证明绑定的trace文本，用于独立追加补证')
    args = parser.parse_args()
    try:
        if args.original_trace:
            from app.governance.archive_trace_supplement import create
            report = create(args.root, args.change, args.original_trace.read_text(), apply=args.apply)
        else:
            report = restore(args.root, args.change, apply=args.apply)
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(json.dumps({'status': 'blocked', 'reason': str(error)}, ensure_ascii=False))
        return 1
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
