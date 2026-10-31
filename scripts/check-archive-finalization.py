#!/usr/bin/env python3
"""只读检查单项归档收尾；成功不代表获得归档授权或通过业务验收。"""
import argparse
import json
from pathlib import Path
import sys

from archive_runtime import repository_root, TOOL_ROOT
ROOT = repository_root(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(TOOL_ROOT / 'src/backend'))
from app.governance.archive_finalization import build_report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--change', required=True)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    report = build_report(args.root, args.change)
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report['status'] == 'finalized' else 1


if __name__ == '__main__':
    raise SystemExit(main())
