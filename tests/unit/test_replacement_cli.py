"""Online CLI cannot turn local files or a timeout into write authorization."""
import json
from pathlib import Path
import pytest
from app.governance import replacement_cli as cli


def config(tmp_path):
    repo=tmp_path/'repo';repo.mkdir()
    path=tmp_path/'operator.json';path.write_text(json.dumps({'base_url':'http://127.0.0.1:39046','access_token':'synthetic-session'}));path.chmod(0o600)
    return repo,path


@pytest.mark.parametrize('damage',['repo','mode','symlink','http','redirect_credentials'])
def test_config_boundary(tmp_path,damage):
    repo,path=config(tmp_path)
    if damage=='repo':target=repo/'operator.json';path.rename(target);path=target
    if damage=='mode':path.chmod(0o644)
    if damage=='symlink':target=tmp_path/'alias';target.symlink_to(path);path=target
    if damage in {'http','redirect_credentials'}:
        value=json.loads(path.read_text());value['base_url']='http://outside.invalid' if damage=='http' else 'https://user:secret@example.invalid';path.write_text(json.dumps(value))
    with pytest.raises(ValueError):cli.configuration(path,repo)


def test_readonly_never_posts_and_unavailable_never_falls_back(tmp_path,monkeypatch,capsys):
    repo,path=config(tmp_path);monkeypatch.chdir(repo);calls=[]
    def transport(config,path,payload=None):calls.append((path,payload));return {'decision':'ready'}
    monkeypatch.setattr(cli,'request',transport)
    assert cli.main(['--config',str(path),'--proposal','proposal'])==0
    assert calls==[('replacement-proposals/proposal/admission',None)]
    def unavailable(*args,**kwargs):raise ValueError('online_authority_unavailable_or_request_unverified')
    monkeypatch.setattr(cli,'request',unavailable)
    assert cli.main(['--config',str(path),'--proposal','proposal','--execute','--operation','original','--expected-revision','2','--digest','a'*64])==1
    assert 'synthetic-session' not in capsys.readouterr().out
    assert not list(repo.iterdir())


def test_execute_preserves_exact_original_identity(tmp_path,monkeypatch):
    repo,path=config(tmp_path);monkeypatch.chdir(repo);calls=[]
    def transport(config,path,payload=None):
        calls.append((path,payload))
        return {'decision':'resume'} if payload is None else {'stage':'completed','replayed':True}
    monkeypatch.setattr(cli,'request',transport)
    args=['--config',str(path),'--proposal','proposal','--execute','--operation','original','--expected-revision','2','--digest','a'*64]
    assert cli.main(args)==0
    assert calls[-1][1]=={'proposal_id':'proposal','expected_revision':2,'proposal_digest':'a'*64,'idempotency_key':'original','confirmed':True}


def test_http_blocking_diagnostics_remain_bounded(monkeypatch):
    import io
    from urllib.error import HTTPError
    from app.governance.archive_diagnostics import ArchiveDiagnosticError
    data = {'reason': 'archive_finalization_blocked', 'operation_id': 'original', 'findings': [
        {'relative_path': 'issues/test.md', 'kind': 'broken-link', 'line': 2, 'message': 'secret raw prose'},
        {'relative_path': '/private/secret', 'kind': 'broken-link'}]}
    class Transport:
        def open(self, *a, **k):
            raise HTTPError('http://localhost',409,'blocked',{},io.BytesIO(json.dumps({'data':data}).encode()))
    monkeypatch.setattr('urllib.request.build_opener', lambda *a: Transport())
    with pytest.raises(ArchiveDiagnosticError) as error:
        cli.request({'base_url':'http://localhost','access_token':'synthetic'},'archive-commands',{})
    assert str(error.value) == 'archive_finalization_blocked'
    assert error.value.details['operation_id'] == 'original'
    assert len(error.value.details['findings']) == 1
    assert 'secret' not in json.dumps(error.value.details)
