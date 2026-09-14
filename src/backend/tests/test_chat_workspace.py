from pathlib import Path
from uuid import uuid4
import os
import subprocess
import pytest
from app.chat.workspace import WorkspaceError, prepare_workspace, workspace_path, snapshot, difference


def test_two_round_diff_has_distinct_cumulative_baseline(tmp_path):
    root=tmp_path.resolve();(root/'counter').write_text('0\n')
    initial=snapshot(root);(root/'counter').write_text('1\n');first=snapshot(root)
    (root/'counter').write_text('2\n');(root/'new.bin').write_bytes(b'\0data');second=snapshot(root)
    delta=difference(first,second);cumulative=difference(initial,second)
    assert '-1\n+2\n' in delta['files'][0]['patch']
    assert '-0\n+2\n' in cumulative['files'][0]['patch']
    assert delta['files'][1]['reason']=='二进制文件'
    assert difference(second,second)['files']==[]
    (root/'counter').unlink();assert difference(second,snapshot(root))['files'][0]['status']=='deleted'


def test_snapshot_never_follows_links_or_special_files(tmp_path):
    root=tmp_path.resolve();inside=root/'workspace';inside.mkdir();outside=root/'private';outside.write_text('never expose')
    (inside/'link').symlink_to(outside)
    data=snapshot(inside);assert data['files']['link']['kind']=='symlink'
    assert 'never expose' not in str(data) and str(outside) not in str(data)
    (inside/'link').unlink();os.link(outside,inside/'hardlink')
    with pytest.raises(WorkspaceError): snapshot(inside)
    (inside/'hardlink').unlink();os.mkfifo(inside/'pipe')
    with pytest.raises(WorkspaceError): snapshot(inside)


def test_limits_preserve_metadata_without_fake_text(tmp_path):
    root=tmp_path.resolve();(root/'large').write_text('a'*100)
    before=snapshot(root,text_bytes=10);assert before['files']['large']['text'] is None
    (root/'large').write_text('b'*100);delta=difference(before,snapshot(root,text_bytes=10))
    assert delta['files'][0]['patch'] is None and delta['files'][0]['after_size']==100
    with pytest.raises(WorkspaceError): snapshot(root,max_total_bytes=10)


def test_workspace_copies_only_committed_tree_and_preserves_source(tmp_path):
    root=tmp_path.resolve();source=root/'source';source.mkdir();workspaces=root/'workspaces';workspaces.mkdir()
    subprocess.run(['git','init','-q',str(source)],check=True)
    (source/'code.txt').write_text('base\n')
    subprocess.run(['git','-C',str(source),'add','code.txt'],check=True)
    subprocess.run(['git','-C',str(source),'-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','fixture'],check=True)
    (source/'.env').write_text('synthetic untracked secret')
    cid=str(uuid4());result=prepare_workspace(source,workspaces,cid)
    assert not (result['path']/'.env').exists()
    assert subprocess.check_output(['git','-C',str(result['path']),'status','--porcelain']) == b''
    (result['path']/'code.txt').write_text('changed\n')
    assert (source/'code.txt').read_text()=='base\n'
    assert workspace_path(workspaces,cid)==result['path']
    with pytest.raises(WorkspaceError): prepare_workspace(source,workspaces,cid)
    with pytest.raises(WorkspaceError): workspace_path(workspaces,'../source')
    linked=workspaces/str(uuid4());linked.symlink_to(source,target_is_directory=True)
    with pytest.raises(WorkspaceError): workspace_path(workspaces,linked.name)


def test_exact_rename_records_old_path(tmp_path):
    root=tmp_path.resolve();(root/'old').write_text('same\n');before=snapshot(root)
    (root/'old').rename(root/'new');files=difference(before,snapshot(root))['files']
    assert len(files)==1 and files[0]['status']=='renamed' and files[0]['previous_path']=='old'
