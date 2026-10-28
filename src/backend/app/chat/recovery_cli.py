"""Deployment operator entry: inspect by default, explicit bounded resume only."""
import argparse
import hashlib
import json
import os
from pathlib import Path
from sqlalchemy import select
from app.db.session import get_session_factory
from app.chat.recovery_schema import recoveries
from app.chat.recovery import resume


def operator_allowed():
    path = Path(os.environ.get('MOONBOX_CHAT_STATE_ROOT', '/nonexistent'))
    return os.getuid() != 0 and not path.is_symlink() and path.is_dir() and path.stat().st_uid == os.getuid() and not path.stat().st_mode & 0o022


def main():
    parser = argparse.ArgumentParser(description='Inspect or explicitly resume one paused Chat recovery')
    parser.add_argument('--turn', required=True)
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--generation', type=int)
    parser.add_argument('--request-id')
    parser.add_argument('--reason', choices=('evidence_updated', 'configuration_fixed', 'operator_reviewed'))
    args = parser.parse_args()
    if not operator_allowed(): parser.error('recovery_operator_required')
    with get_session_factory()() as db:
        if args.resume:
            if args.generation is None or not args.request_id or not args.reason: parser.error('resume_fields_required')
            try:
                resume(db, args.turn, args.generation, args.request_id, 'uid:'+str(os.getuid()), args.reason, authorize=operator_allowed)
            except (ValueError, PermissionError): parser.error('recovery_resume_rejected')
        row = db.execute(select(recoveries).where(recoveries.c.turn_id == args.turn)).mappings().first()
        if not row: parser.error('recovery_not_found')
        print(json.dumps({key: row[key] for key in ('state','generation','attempt_count','next_retry_at','last_result')}))


if __name__ == '__main__': main()
