"""Private opaque records, never source paths in public records or generic logs."""
import json
import os
import stat
from pathlib import Path
from uuid import UUID
from app.chat.workspace import trusted_directory, WorkspaceError
from app.chat.service import ChatError


def root():
    value=os.environ.get('MOONBOX_GOVERNANCE_STATE_ROOT','')
    if not value: raise ChatError(2605,'治理成果存储尚未配置',503)
    try:
        directory=trusted_directory(value)
        if directory.stat().st_mode & 0o077: raise WorkspaceError('permissions')
        return directory
    except (OSError,WorkspaceError): raise ChatError(2605,'治理成果存储不可用',503) from None


def identifier(value):
    try: return str(UUID(value))
    except (ValueError,TypeError,AttributeError): raise ChatError(2604,'无效成果标识',422) from None


def write(record_id, name, value):
    if name not in ('baseline','result','operation'): raise ValueError('record_name')
    base=root()/identifier(record_id)
    base.mkdir(mode=0o700,exist_ok=True);trusted_directory(base)
    fd=os.open(base,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:
        tmp=name+'.tmp'
        try:
            out=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=fd)
        except FileExistsError:
            previous=os.open(tmp,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=fd)
            with os.fdopen(previous) as stream:
                info=os.fstat(stream.fileno())
                if not stat.S_ISREG(info.st_mode) or info.st_nlink!=1 or info.st_size>64*1024*1024:
                    raise ValueError('unrecognized_private_temporary')
                pending=json.load(stream)
            # A stale prepared/phase log may be replaced only when immutable inputs match.
            if {k:v for k,v in pending.items() if k!='phase'} != {k:v for k,v in value.items() if k!='phase'}:
                raise ValueError('unrecognized_private_temporary')
            os.unlink(tmp,dir_fd=fd);os.fsync(fd)
            out=os.open(tmp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=fd)
        try:
            with os.fdopen(out,'w') as stream:
                json.dump(value,stream,ensure_ascii=False);stream.flush();os.fsync(stream.fileno())
            os.replace(tmp,name+'.json',src_dir_fd=fd,dst_dir_fd=fd);os.fsync(fd)
        finally:
            try: os.unlink(tmp,dir_fd=fd)
            except FileNotFoundError: pass
    finally: os.close(fd)


def read(record_id,name):
    if name not in ('baseline','result','operation'): raise ValueError('record_name')
    base=trusted_directory(root()/identifier(record_id))
    fd=os.open(base,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:
        handle=os.open(name+'.json',os.O_RDONLY|os.O_NOFOLLOW,dir_fd=fd)
        with os.fdopen(handle) as stream:
            info=os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_nlink!=1 or info.st_size>64*1024*1024:
                raise ValueError('unsafe_private_record')
            return json.load(stream)
    finally: os.close(fd)
