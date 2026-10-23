"""Online archive client; no signing keys, database access or local file writes.

The operator supplies an existing session in a private config outside the
repository. This client cannot approve proposals or establish deployment trust.
"""
import argparse
import json
import os
from pathlib import Path
import re
import stat
import sys
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from .replacement_proof import strict_json, canonical


def configuration(path, repository):
    path = Path(path)
    if not path.is_absolute() or path.resolve().is_relative_to(repository.resolve()):
        raise ValueError('private_operator_config_required')
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('private_operator_config_required')
    with os.fdopen(os.open(path, os.O_RDONLY | os.O_NOFOLLOW), 'rb') as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_mode & 0o077 or info.st_uid != os.getuid():
            raise ValueError('private_operator_config_required')
        value = strict_json(stream.read(16385))
    if set(value) != {'base_url', 'access_token'} or not all(isinstance(v, str) and v for v in value.values()):
        raise ValueError('invalid_operator_config')
    url = urlsplit(value['base_url'])
    if (url.username or url.password or url.query or url.fragment or url.path not in {'', '/'}
            or url.scheme != 'https' and not (url.scheme == 'http' and url.hostname in {'localhost', '127.0.0.1', '::1'})
            or '\n' in value['access_token'] or '\r' in value['access_token']):
        raise ValueError('invalid_operator_endpoint')
    return value


def request(config, path, payload=None):
    # Redirects must not forward the operator's session to another origin.
    from urllib.request import build_opener, HTTPRedirectHandler
    class NoRedirect(HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):
            raise ValueError('operator_endpoint_redirected')
    req = Request(config['base_url'].rstrip('/') + '/api/v1/chat/' + path,
        data=canonical(payload) if payload is not None else None,
        headers={'Authorization': 'Bearer ' + config['access_token'], 'Content-Type': 'application/json'})
    try:
        with build_opener(NoRedirect).open(req, timeout=60) as response:
            result = strict_json(response.read(262145))
    except (HTTPError, URLError, TimeoutError, OSError):
        raise ValueError('online_authority_unavailable_or_request_unverified') from None
    if result.get('code') != 0 or not isinstance(result.get('data'), dict):
        raise ValueError('invalid_authority_response')
    return result['data']


def main(argv=None):
    parser = argparse.ArgumentParser(description='在线核验或执行已批准的规则替代；不进行批准。')
    parser.add_argument('--config', required=True)
    target=parser.add_mutually_exclusive_group(required=True)
    target.add_argument('--proposal')
    target.add_argument('--object')
    parser.add_argument('--space')
    parser.add_argument('--repository')
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--operation')
    parser.add_argument('--expected-revision', type=int)
    parser.add_argument('--digest')
    args = parser.parse_args(argv)
    try:
        config = configuration(args.config, Path.cwd())
        if args.object:
            if (not args.execute or not args.space or not args.repository
                    or not re.fullmatch(r'(?:(?:REQ|BUG)-\d{4}-[A-Za-z0-9_-]+|[a-z0-9][a-z0-9-]{0,100})',args.object)):
                raise ValueError('explicit_object_execution_required')
            result=request(config,'archive-commands',{'space_id':args.space,'repository_id':args.repository,
                'object_id':args.object,'confirmed':True})
            print(json.dumps(result,ensure_ascii=False))
            return 0 if result.get('stage')=='completed' else 1
        if not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', args.proposal):
            raise ValueError('invalid_proposal_identity')
        admission = request(config, 'replacement-proposals/' + args.proposal + '/admission')
        if not args.execute:
            print(json.dumps(admission, ensure_ascii=False))
            return 0 if admission.get('decision') == 'ready' else 1
        if (not re.fullmatch(r'[A-Za-z0-9_-]{1,64}', args.operation or '')
                or not args.expected_revision or args.expected_revision < 1
                or not re.fullmatch(r'[a-f0-9]{64}', args.digest or '')):
            raise ValueError('exact_original_operation_required')
        if admission.get('decision') not in {'ready', 'resume'}:
            print(json.dumps(admission, ensure_ascii=False))
            return 1
        result = request(config, 'replacement-archive-operations', {
            'proposal_id': args.proposal, 'expected_revision': args.expected_revision,
            'proposal_digest': args.digest, 'idempotency_key': args.operation, 'confirmed': True})
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result.get('stage') == 'completed' else 1
    except ValueError as error:
        # Error codes are local constants; never include HTTP bodies or tokens.
        print(json.dumps({'decision': 'blocked', 'reason_code': str(error),
            'guidance': '核验在线服务；结果未知时保持原提案、版本、摘要和 operation，不创建新操作。'}, ensure_ascii=False))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
