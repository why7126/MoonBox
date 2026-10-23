"""Operator CLI sharing the product's authenticated completion verifier.

Run inside the configured service environment. No direct guard/database edits.
"""
import argparse
import json
from app.db.session import get_session_factory
from app.governance.direct_completion import status, recover, DirectProofError
from app.chat.service import ChatError


def main():
    parser = argparse.ArgumentParser(description='核验直接命令当前成果；不重放业务')
    parser.add_argument('--actor', required=True)
    parser.add_argument('--turn', required=True)
    parser.add_argument('--expected-version', type=int)
    parser.add_argument('--recover', action='store_true')
    args = parser.parse_args()
    if args.recover and args.expected_version is None:
        parser.error('恢复需要 --expected-version')
    try:
        with get_session_factory()() as db:
            result = (recover(db, args.actor, args.turn, args.expected_version)
                      if args.recover else status(db, args.actor, args.turn))
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result['state'] in ('validated', 'recovered_valid') else 1
    except (DirectProofError, ChatError) as error:
        reason = str(error) if isinstance(error, DirectProofError) else (getattr(error, 'kind', None) or 'verification_failed')
        print(json.dumps({'state':'blocked','reason_code':reason},ensure_ascii=False))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
