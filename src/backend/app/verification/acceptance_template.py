"""Deployment-only approval for full Chat acceptance capabilities."""
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
from app.verification.candidate_template import CandidateTemplate, CandidateError, digest
from app.verification.acceptance_state import Conflict


@dataclass(frozen=True)
class AcceptanceTemplate:
    data: dict

    @property
    def key(self):
        return digest(self.data)

    @classmethod
    def parse(cls, data):
        required = {'schema_version','template','base','node_image','runtime_versions',
                    'roles','checks','disk_strategy','deployment_digest','identity_adapter'}
        if not isinstance(data,dict) or set(data) != required or data['schema_version'] != 1:
            raise Conflict('acceptance_template_invalid')
        if data['template'] != 'moonbox-chat-acceptance-v1' or data['disk_strategy'] != 'bounded-tmpfs':
            raise Conflict('acceptance_template_unsupported')
        try:
            CandidateTemplate.parse(data['base'])
        except CandidateError:
            raise Conflict('acceptance_base_template_invalid') from None
        if not re.fullmatch(r'sha256:[a-f0-9]{64}',str(data['node_image'])):
            raise Conflict('acceptance_image_unpinned')
        if not re.fullmatch(r'[a-f0-9]{64}',str(data['deployment_digest'])):
            raise Conflict('deployment_version_unpinned')
        versions = data['runtime_versions']
        if not isinstance(versions,dict) or set(versions) != {'python','node','mysql','chromium','firefox'}:
            raise Conflict('runtime_versions_missing')
        if any(not isinstance(v,str) or not re.fullmatch(r'[0-9]+(?:\.[0-9]+){1,3}',v) for v in versions.values()):
            raise Conflict('runtime_versions_unpinned')
        if not versions['mysql'].startswith('8.4.'):
            raise Conflict('mysql_version_unsupported')
        if (not isinstance(data['roles'],list) or any(not isinstance(role,str) for role in data['roles'])
                or not {'member','reader'} <= set(data['roles']) <= {'member','reader','admin'}):
            raise Conflict('identity_roles_invalid')
        if not isinstance(data['checks'],dict) or not 1 <= len(data['checks']) <= 200:
            raise Conflict('approved_checks_missing')
        for ac, check in data['checks'].items():
            if not re.fullmatch(r'AC-[A-Z0-9-]{1,60}',ac) or not isinstance(check,dict):
                raise Conflict('approved_check_invalid')
            if set(check) != {'argv','database','role'} or check['database'] not in {'sqlite','mysql'} or check['role'] not in data['roles']:
                raise Conflict('approved_check_invalid')
            argv = check['argv']
            if not isinstance(argv,list) or not 1 <= len(argv) <= 32 or argv[0] not in {'python','pytest','node'}:
                raise Conflict('approved_command_invalid')
            if any(not isinstance(a,str) or not a or '\x00' in a or len(a)>4096 for a in argv):
                raise Conflict('approved_command_invalid')
        adapter=data['identity_adapter']
        if not isinstance(adapter,dict) or set(adapter)!={'issue','revoke','login'}:
            raise Conflict('identity_adapter_invalid')
        for argv in (adapter['issue'],adapter['revoke']):
            if (not isinstance(argv,list) or not 1<=len(argv)<=32 or argv[0] not in {'python','node'}
                    or any(not isinstance(a,str) or not a or '\x00' in a or len(a)>4096 for a in argv)):
                raise Conflict('identity_adapter_invalid')
        login=adapter['login']
        if (not isinstance(login,dict) or set(login)!={'path','username_field','password_field'}
                or not re.fullmatch(r'/[a-zA-Z0-9/_-]+',str(login['path']))
                or any(not re.fullmatch(r'[a-zA-Z_][a-zA-Z0-9_]{0,63}',str(login[k])) for k in ('username_field','password_field'))):
            raise Conflict('identity_login_invalid')
        return cls(data)


def approved_template(source_root=None):
    value = os.getenv('MOONBOX_ACCEPTANCE_TEMPLATE')
    if not value: raise Conflict('acceptance_template_unavailable')
    path = Path(value)
    if (not path.is_absolute() or path.is_symlink() or not path.is_file()
            or path.stat().st_mode & 0o022 or path.stat().st_size > 256 * 1024
            or source_root is not None and path.resolve().is_relative_to(Path(source_root).resolve())):
        raise Conflict('acceptance_template_untrusted')
    try:
        return AcceptanceTemplate.parse(json.loads(path.read_text()))
    except (OSError,UnicodeError,json.JSONDecodeError):
        raise Conflict('acceptance_template_invalid') from None
