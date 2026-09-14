"""日常脚本的受控Chat测试入口；Unix控制通道，不使用持久化PID杀进程。"""
import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import socket
import stat
import subprocess
import sys
import time

PROJECT = Path(__file__).resolve().parents[4]


def control_root(scope):
    key=hashlib.sha256((str(PROJECT)+'\n'+str(Path(scope).absolute())).encode()).hexdigest()[:20]
    return Path('/tmp').resolve()/('moonbox-chat-control-'+key)


def private_root(root, create=False):
    if create:root.mkdir(mode=0o700,exist_ok=True)
    info=root.lstat()
    if not stat.S_ISDIR(info.st_mode) or info.st_uid!=os.getuid() or info.st_mode & 0o077:
        raise RuntimeError('控制目录权限无效')


def request(root, action):
    private_root(root)
    with socket.socket(socket.AF_UNIX) as client:
        client.settimeout(4)
        client.connect(str(root/'control.sock'))
        client.sendall(action.encode()+b'\n')
        data=client.recv(16384)
    return json.loads(data)


@contextmanager
def lock(root):
    private_root(root,True)
    fd=os.open(root/'operation.lock',os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'w') as file:
        fcntl.flock(file,fcntl.LOCK_EX)
        yield


def existing(root):
    if not root.exists():return None
    private_root(root)
    if not (root/'control.sock').exists():
        if (root/'starting').exists():raise RuntimeError('Chat实例正在启动或已失联；请检查原启动记录，不覆盖状态')
        return None
    try:
        result=request(root,'status')
        return result
    except (OSError,ValueError):raise RuntimeError('Chat控制端失联；保留现场，不按旧PID终止未知进程')


def preflight(root):
    active=existing(root)
    if active:
        if not active.get('ready'):raise RuntimeError('Chat进程存在但未就绪；请先停止并检查启动依赖')
        return active
    if sys.version_info<(3,12):raise RuntimeError('Chat控制器需要Python 3.12或以上，请设置PYTHON_BIN')
    if os.getuid()==0:raise RuntimeError('Chat控制器需要非root用户')
    for module in ('sqlalchemy','fastapi','uvicorn','yaml','pydantic'):
        if importlib.util.find_spec(module) is None:raise RuntimeError('Python后端依赖缺失；请使用已安装src/backend依赖的PYTHON_BIN')
    auth=Path.home()/'.codex/auth.json'
    if auth.is_symlink() or not auth.is_file() or auth.stat().st_uid!=os.getuid():
        raise RuntimeError('本地Codex认证文件不可用，请先完成本地登录')
    if not shutil.which('git') or not shutil.which('docker'):raise RuntimeError('需要Git和Docker')
    result=subprocess.run(['docker','info','--format','{{.OSType}}'],capture_output=True,text=True,timeout=15)
    if result.returncode or result.stdout.strip()!='linux':raise RuntimeError('Docker Linux引擎不可用')
    port=int(os.environ.get('HOST_PORT_CHAT_TEST','18121'))
    if not 18101<=port<=18199:raise RuntimeError('Chat测试端口需要位于18101–18199')
    with socket.socket() as probe:
        try:probe.bind(('127.0.0.1',port))
        except OSError:raise RuntimeError('Chat测试端口已占用；不会停止占用端口的其他服务')
    return None


def start(root, image):
    with lock(root):
        active=preflight(root)
        if active:return {**active,'already_running':True}
        dist=root/'web-dist'
        if dist.exists():shutil.rmtree(dist)
        # Copy static assets from the just-built Web image, never a real container volume.
        container=subprocess.check_output(['docker','create',image],text=True).strip()
        try:
            subprocess.run(['docker','cp',container+':/usr/share/nginx/html',str(dist)],check=True,capture_output=True)
        finally:subprocess.run(['docker','rm',container],check=True,capture_output=True)
        if not (dist/'index.html').is_file():raise RuntimeError('Web镜像缺少构建产物')
        marker=root/'starting';marker.write_text('starting');marker.chmod(0o600)
        env={**os.environ,'CHAT_LIVE_ISOLATED_PROBE':'1','MOONBOX_CHAT_TEST_EXECUTOR':'container',
             'MOONBOX_CHAT_CONTROL_SOCKET':str(root/'control.sock'),'MOONBOX_CHAT_TEST_WEB_DIST':str(dist)}
        # Harness owns worker/API/temp data; it expires after one hour even without a caller.
        process=subprocess.Popen([sys.executable,str(PROJECT/'src/backend/tests/chat_isolated_harness.py')],
            env=env,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,start_new_session=True,cwd=PROJECT)
        deadline=time.monotonic()+40
        while time.monotonic()<deadline:
            if process.poll() is not None:
                marker.unlink(missing_ok=True)
                raise RuntimeError('Chat启动失败，未就绪；常规服务可能已启动')
            try:
                result=request(root,'status')
                if not result.get('ready'):raise RuntimeError('Chat进程未就绪')
                marker.unlink(missing_ok=True)
                return result
            except (OSError,ValueError):time.sleep(.2)
        process.terminate()
        try:process.wait(timeout=80)
        except subprocess.TimeoutExpired:raise RuntimeError('Chat启动超时，仍需检查原进程；保留启动标记')
        marker.unlink(missing_ok=True)
        raise RuntimeError('Chat未在启动窗口内就绪')


def stop(root):
    with lock(root):
        active=existing(root)
        if not active:return {'stopped':True,'already_stopped':True}
        request(root,'cleanup')
        deadline=time.monotonic()+100
        while (root/'control.sock').exists() and time.monotonic()<deadline:time.sleep(.2)
        if (root/'control.sock').exists():raise RuntimeError('Chat仍在停止，未停止常规服务；请稍后重试')
        dist=root/'web-dist'
        if dist.is_dir() and not dist.is_symlink():shutil.rmtree(dist)
        return {'stopped':True,'test_data_removed':not Path(active['root']).exists()}


def main():
    parser=argparse.ArgumentParser(description='独立Chat测试环境控制')
    parser.add_argument('--scope',required=True)
    sub=parser.add_subparsers(dest='action',required=True)
    sub.add_parser('check');sub.add_parser('stop');sub.add_parser('status')
    create=sub.add_parser('start');create.add_argument('--web-image',required=True)
    args=parser.parse_args();root=control_root(args.scope)
    try:
        if args.action=='start':result=start(root,args.web_image)
        elif args.action=='stop':result=stop(root)
        elif args.action=='status':result=existing(root) or {'running':False}
        else:result=preflight(root) or {'preflight':True}
        print(json.dumps(result,ensure_ascii=False))
    except Exception as error:
        # Only our stable messages are user-facing; subprocess errors may contain env paths.
        message=str(error) if type(error) is RuntimeError else 'Chat部署操作未完成，请检查依赖、端口和私有控制目录'
        raise SystemExit(message)


if __name__=='__main__':main()
