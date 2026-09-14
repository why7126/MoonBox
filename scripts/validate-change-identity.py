#!/usr/bin/env python3
"""校验活动/归档 Change ID 唯一性；--new-id 用于创建前占用检查。"""
import argparse
from pathlib import Path
from change_identity import validate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1], help='仓库根目录（支持隔离测试）')
    parser.add_argument('--new-id', help='创建前检查候选 ID，活动和归档均不可复用')
    args = parser.parse_args()
    errors = validate(args.root, args.new_id)
    for error in errors:
        print(error)
    print('Change 身份校验失败。' if errors else 'Change 身份校验通过。')
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
