"""显式常驻部署的本机预检和目录准备；不创建用户、不选择仓库、不输出凭证。"""
import json
import os
from pathlib import Path
import re
import stat
import sys
from app.chat.workspace import trusted_directory, git


def mapping():
    repository=os.environ.get('MOONBOX_CHAT_REPOSITORY_ID','')
    space=os.environ.get('MOONBOX_CHAT_SPACE_ID','')
    if any(not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}',value) for value in (repository,space)):
        raise ValueError('请配置目标仓库标识和已有空间ID')
    root=Path(os.environ['MOONBOX_CHAT_HOST_ROOT'])
    source=Path(os.environ.get('MOONBOX_CHAT_SOURCE_ROOT',''))
    if not root.is_absolute() or not source.is_absolute(): raise ValueError('需配置绝对路径的仓库和私有数据目录')
    return {'id':repository,'space_id':space,'source_root':str(source),'workspace_root':str(root/'workspaces'),
            'governance_root':'/app/governance'}


def check():
    from app.chat.settings import execution_limits, retention_limits
    if os.getuid()==0: raise ValueError('执行控制器需要非root部署用户')
    row=mapping();source=trusted_directory(row['source_root'])
    git(source,'rev-parse','--verify','HEAD')
    root=Path(os.environ['MOONBOX_CHAT_HOST_ROOT'])
    for part in [*reversed(root.parents),root]:
        if part.is_symlink(): raise ValueError('私有数据目录不能包含符号链接')
    if source==root or root in source.parents: raise ValueError('源仓库不能位于执行数据目录内')
    if source in root.parents:
        git(source,'check-ignore','-q',str(root/'workspaces'))
    auth=Path(os.environ['MOONBOX_CHAT_AUTH_SOURCE'])
    info=auth.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid!=os.getuid(): raise ValueError('本机Codex认证文件不可用')
    if execution_limits() is None or retention_limits() is None: raise ValueError('额度或保留策略缺失或无效')
    if root.exists() and root.stat().st_mode & 0o077: raise ValueError('私有数据目录需要0700权限')
    return row


def prepare():
    check();root=Path(os.environ['MOONBOX_CHAT_HOST_ROOT'])
    root.mkdir(mode=0o700,parents=True,exist_ok=True)
    for name in ('state','runtime','backups','workspaces'):
        path=root/name;path.mkdir(mode=0o700,exist_ok=True);trusted_directory(path)
        if path.stat().st_mode & 0o077: raise ValueError('私有子目录需要0700权限')
    from app.chat.backup import LocalBackupStore
    backup=root/'backups'
    LocalBackupStore(backup,initialize=not (backup/'deletions.sqlite').exists())


def main():
    action=sys.argv[1]
    if action in ('catalog','bindings'):
        row=mapping()
        if action=='catalog':row={key:row[key] for key in ('id','space_id')}
        print(json.dumps([row]))
    elif action=='check':check();print('Chat常驻部署配置预检通过')
    elif action=='prepare':prepare();print('Chat私有运行目录和独立备份日志已就绪')
    else:raise ValueError('未知操作')

if __name__=='__main__':
    try:main()
    except Exception:raise SystemExit('Chat常驻部署配置无效：检查仓库/空间标识、绝对路径、目录权限、本机凭证及额度配置') from None
