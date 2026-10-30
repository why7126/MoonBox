#!/usr/bin/env python3
"""校验已归档验收元数据；--apply 追加绑定证明，不修改历史原文或恢复日志。"""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src/backend'))
from app.governance.archive_metadata import restore


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--change', required=True)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--apply', action='store_true', help='追加不可覆盖的验收状态恢复记录')
    args = parser.parse_args()
    try:
        report = restore(args.root, args.change, apply=args.apply)
    except (OSError, ValueError, TypeError, KeyError) as error:
        print(json.dumps({'status': 'blocked', 'reason': str(error)}, ensure_ascii=False))
        return 1
    print(json.dumps(report, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
