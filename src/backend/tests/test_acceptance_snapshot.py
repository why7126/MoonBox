import os
import pytest
from app.verification.acceptance_snapshot import capture
from app.verification.acceptance_state import Conflict


def test_uncommitted_content_and_deletion_are_in_fingerprint(tmp_path):
    path=tmp_path/'app.py';path.write_text('before')
    first=capture(tmp_path,['app.py'],binding='b',head_commit='h')
    path.write_text('after')
    second=capture(tmp_path,['app.py'],binding='b',head_commit='h')
    assert first['digest']!=second['digest']
    assert second['content']['app.py'][0]==b'after'
    path.unlink()
    assert capture(tmp_path,['app.py'],binding='b',head_commit='h')['manifest']==[['app.py',None,None]]


@pytest.mark.parametrize('path',['../secret','.env','.env.production','.ssh/id_rsa','data.sqlite','/tmp/file'])
def test_sensitive_or_escaping_scope_rejected(tmp_path,path):
    with pytest.raises(Conflict):capture(tmp_path,[path],binding='b',head_commit='h')


def test_links_rejected(tmp_path):
    (tmp_path/'source').write_text('safe')
    (tmp_path/'link').symlink_to(tmp_path/'source')
    with pytest.raises(Conflict):capture(tmp_path,['link'],binding='b',head_commit='h')
    os.link(tmp_path/'source',tmp_path/'hard')
    with pytest.raises(Conflict):capture(tmp_path,['hard'],binding='b',head_commit='h')


def test_unowned_paths_not_captured(tmp_path):
    (tmp_path/'owned').write_text('safe');(tmp_path/'other').write_text('private')
    assert set(capture(tmp_path,['owned'],binding='b',head_commit='h')['content'])=={'owned'}
