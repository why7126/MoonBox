"""Focused acceptance entry: verify immutable product evidence and run regressions."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[3]
CHANGE=ROOT/'openspec/changes/fix-chat-midrun-question-response'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--preflight',action='store_true');args=parser.parse_args()
    assert (ROOT/'src/web/node_modules/@playwright/test').exists(), 'browser dependency missing'
    if args.preflight:
        print('browser dependency and isolated evidence entry available');return
    styles=json.loads((CHANGE/'evidence/acceptance/browser/computed-styles.json').read_text())
    assert len(styles['samples'])==16 and not any(x['overflow'] for x in styles['samples'])
    for sample in styles['samples']:
        assert (CHANGE/f"evidence/acceptance/browser/{sample['state']}-{sample['viewport']}.png").is_file()
        assert sample['border'].startswith('1px')
    live=json.loads((CHANGE/'evidence/acceptance/browser/live-result.json').read_text())
    assert live['state']=='completed' and live['answer_matches'] and live['question_states']==['delivered'] and live['error_code'] is None
    mysql=json.loads((CHANGE/'evidence/acceptance/manual/mysql.json').read_text())
    assert mysql['exit_code']==0 and mysql['passed']>=21
    for relative,digest in mysql['inputs'].items():assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==digest
    env=__import__('os').environ.copy();env['PYTHONPATH']=str(ROOT/'src/backend');env.pop('CHAT_TEST_DATABASE_URL',None)
    result=subprocess.run([sys.executable,'-m','pytest','src/backend/tests/test_chat_questions.py','src/backend/tests/test_chat_app_server.py','-q','--tb=short'],cwd=ROOT,env=env)
    if result.returncode:raise SystemExit(result.returncode)
    result=subprocess.run([str(ROOT/'src/web/node_modules/.bin/vitest'),'run','src/components/chat/QuestionPanel.test.tsx'],cwd=ROOT/'src/web')
    raise SystemExit(result.returncode)

if __name__=='__main__':main()
