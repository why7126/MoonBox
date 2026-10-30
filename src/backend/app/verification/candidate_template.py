"""Deployment-approved plans. Candidate checkouts and HTTP requests cannot supply one."""
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re


class CandidateError(ValueError):
    pass


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def relative(value):
    if not isinstance(value, str) or not value or '\\' in value:
        raise CandidateError('template_path_invalid')
    path = PurePosixPath(value)
    if path.is_absolute() or any(p in ('..', '.', '') for p in value.split('/')):
        raise CandidateError('template_path_invalid')
    return value


@dataclass(frozen=True)
class CandidateTemplate:
    data: dict

    @property
    def key(self):
        return digest(self.data)

    @classmethod
    def parse(cls, data):
        fields = {'schema_version', 'template', 'platform', 'python_image', 'mysql_image', 'browser_image',
                  'source_subdir', 'app_module', 'health_path', 'lock_path', 'lock_digest',
                  'migration', 'seed', 'checks', 'browser', 'viewports', 'selectors', 'steps'}
        if not isinstance(data, dict) or set(data) != fields or data['schema_version'] != 1:
            raise CandidateError('template_invalid')
        if data['template'] != 'moonbox-web-python-v1' or data['platform'] != 'linux/arm64':
            raise CandidateError('template_platform_unsupported')
        for key in ('python_image', 'mysql_image', 'browser_image'):
            if not isinstance(data[key], str) or not re.fullmatch(r'sha256:[a-f0-9]{64}', data[key]):
                raise CandidateError('template_image_unpinned')
        for key in ('source_subdir', 'lock_path'):
            relative(data[key])
        if not isinstance(data['lock_digest'], str) or not re.fullmatch(r'[a-f0-9]{64}', data['lock_digest']):
            raise CandidateError('template_dependencies_unpinned')
        if not isinstance(data['app_module'], str) or not re.fullmatch(r'[a-zA-Z_][\w.]*:[a-zA-Z_]\w*', data['app_module']):
            raise CandidateError('template_app_invalid')
        if not isinstance(data['health_path'], str) or not re.fullmatch(r'/[a-zA-Z0-9/_-]*', data['health_path']):
            raise CandidateError('template_health_invalid')
        # Only deployment operators approve argument arrays. No shell expansion.
        commands = [data['migration'], data['seed'], *data['checks']] if isinstance(data['checks'], list) else []
        if not 3 <= len(commands) <= 18:
            raise CandidateError('template_checks_required')
        for command in commands:
            if not isinstance(command, list) or not 1 <= len(command) <= 32 or command[0] not in ('python', 'pytest'):
                raise CandidateError('template_command_invalid')
            if any(not isinstance(x, str) or not x or len(x) > 4096 or '\x00' in x for x in command):
                raise CandidateError('template_command_invalid')
        if data['browser'] not in ('chromium', 'firefox') or not isinstance(data['selectors'], list) or not 1 <= len(data['selectors']) <= 20 or any(not isinstance(x,str) or not x or len(x)>160 for x in data['selectors']):
            raise CandidateError('template_browser_required')
        # Full browser-plan validation is also enforced by the existing runner.
        if not isinstance(data['viewports'], list) or not 1 <= len(data['viewports']) <= 4:
            raise CandidateError('template_browser_required')
        if not isinstance(data['steps'], list) or len(data['steps']) > 20:
            raise CandidateError('template_browser_required')
        return cls(data)


def approved_template():
    name = os.getenv('MOONBOX_CANDIDATE_TEMPLATE')
    if not name:
        raise CandidateError('isolated_candidate_validation_unavailable')
    path = Path(name)
    if not path.is_absolute() or path.is_symlink() or not path.is_file() or path.stat().st_mode & 0o022:
        raise CandidateError('template_not_trusted')
    if path.stat().st_size > 65536:
        raise CandidateError('template_invalid')
    try:
        return CandidateTemplate.parse(json.loads(path.read_text()))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise CandidateError('template_invalid') from exc
