"""Fixed dependency/thread probe shared by worker diagnostics and acceptance."""
PYTHON_PROBE = '"""Bounded external caller runs this probe inside the approved Python image."""\nimport asyncio\nimport json\nfrom importlib.metadata import version\nimport anyio\nimport httpx\nimport pytest\n\nasync def main():\n    with anyio.fail_after(5):\n        assert await anyio.to_thread.run_sync(lambda: 42) == 42\n    print(json.dumps({\'status\':\'ready\',\'versions\':{name:version(name) for name in (\'pytest\',\'httpx\',\'anyio\')}}))\n\nif __name__==\'__main__\':\n    asyncio.run(main())\n'


def probe_image(image_digest):
    """Probe only a deployment-owned immutable image and always remove the exact container."""
    import json
    import os
    import re
    import shutil
    import subprocess
    from uuid import uuid4
    from app.verification.runner import RunnerUnavailable
    if not isinstance(image_digest,str) or not re.fullmatch(r'sha256:[0-9a-f]{64}',image_digest):
        raise RunnerUnavailable('python_image_unpinned')
    docker=shutil.which('docker')
    if not docker:raise RunnerUnavailable('container_runtime_unavailable')
    name='moonbox-python-probe-'+uuid4().hex
    labels=[]
    if os.getenv('MOONBOX_TEMP_RUN') and os.getenv('MOONBOX_TEMP_EXPIRES'):
        labels=['--label','moonbox.temp.managed=true','--label','moonbox.temp.run='+os.environ['MOONBOX_TEMP_RUN'],
                '--label','moonbox.temp.expires='+os.environ['MOONBOX_TEMP_EXPIRES']]
    try:
        response=subprocess.run([docker,'run','--name',name,*labels,'--network','none','--read-only',
            '--cap-drop','ALL','--security-opt','no-new-privileges:true','--cpus','1','--memory','256m',
            '--pids-limit','64','--tmpfs','/tmp:rw,nosuid,size=32m','--user','10001:10001',
            image_digest,'python','-c',PYTHON_PROBE],capture_output=True,text=True,timeout=15)
        if response.returncode:raise RunnerUnavailable('python_test_runtime_unavailable')
        result=json.loads(response.stdout)
        if result.get('status')!='ready' or set(result.get('versions',{}))!={'pytest','httpx','anyio'}:
            raise ValueError()
        return result
    except (OSError,subprocess.TimeoutExpired,ValueError,TypeError):
        raise RunnerUnavailable('python_test_runtime_unavailable') from None
    finally:
        try:
            cleanup=subprocess.run([docker,'rm','--force',name],capture_output=True,timeout=10)
            if cleanup.returncode:
                raise RunnerUnavailable('python_probe_cleanup_unconfirmed')
        except (OSError,subprocess.TimeoutExpired):
            raise RunnerUnavailable('python_probe_cleanup_unconfirmed') from None
