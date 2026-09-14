"""独占子进程组；父worker丢失时收回执行进程，绝不据此推断业务终态。"""
import os
import signal
import subprocess
import sys
import time


def supervise(command):
    parent=os.getppid();stopping=False
    def stop(*_):
        nonlocal stopping
        stopping=True
    signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
    child=subprocess.Popen(command,start_new_session=True)
    try:
        while child.poll() is None and not stopping and os.getppid()==parent:
            time.sleep(.1)
    finally:
        # The group is created here, never restored from a database PID.
        try:os.killpg(child.pid,signal.SIGTERM)
        except (ProcessLookupError,PermissionError):pass
        until=time.monotonic()+2
        while time.monotonic()<until:
            try:os.killpg(child.pid,0)
            except (ProcessLookupError,PermissionError):break
            time.sleep(.05)
        try:os.killpg(child.pid,signal.SIGKILL)
        except (ProcessLookupError,PermissionError):pass
        child.wait()
    return child.returncode

if __name__=='__main__':sys.exit(supervise(sys.argv[1:]))
