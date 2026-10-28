"""输入指纹的跨入口一致性、目录变更与可信路径边界。"""
import shutil
from pathlib import Path
import pytest
from app.governance.acceptance_evidence import fingerprint, input_bytes

@pytest.mark.parametrize('prefix', ['src', 'scripts', 'tests'])
@pytest.mark.parametrize('directory', [False, True])
def test_trusted_source_projection_matches_cli(tmp_path, prefix, directory):
    source, projection = tmp_path/'source', tmp_path/'projection'
    source.mkdir(); projection.mkdir()
    path = source/prefix/'nested/a.py'; path.parent.mkdir(parents=True); path.write_text('same')
    relative = prefix if directory else f'{prefix}/nested/a.py'
    check={'inputs':[relative]}
    assert fingerprint(source,check)==fingerprint(projection,check,source_root=source)
    before=fingerprint(source,check); path.write_text('changed')
    assert fingerprint(projection,check,source_root=source)!=before

@pytest.mark.parametrize('mutation', ['content','add','delete','rename','empty-directory'])
def test_directory_mutation_invalidates_fingerprint(tmp_path, mutation):
    folder=tmp_path/'specs';folder.mkdir();file=folder/'a.md';file.write_text('old')
    check={'inputs':['specs']};before=fingerprint(tmp_path,check)
    if mutation=='content':file.write_text('new')
    elif mutation=='add':(folder/'b.md').write_text('new')
    elif mutation=='delete':file.unlink()
    elif mutation=='rename':file.rename(folder/'b.md')
    else:(folder/'empty').mkdir()
    assert fingerprint(tmp_path,check)!=before

@pytest.mark.parametrize('outside', [True,False])
def test_directory_links_fail_closed(tmp_path,outside):
    folder=tmp_path/'specs';folder.mkdir(); target=tmp_path/'other' if outside else folder/'other'
    target.mkdir();(folder/'link').symlink_to(target,target_is_directory=True)
    with pytest.raises(ValueError):fingerprint(tmp_path,{'inputs':['specs']})

@pytest.mark.parametrize('relative', ['', '.', '../secret','/tmp/secret','tests/../../secret'])
def test_untrusted_paths_rejected(tmp_path,relative):
    with pytest.raises(ValueError):input_bytes(tmp_path,{},relative,source_root=tmp_path)


def test_governance_never_falls_back_to_source(tmp_path):
    source,projection=tmp_path/'source',tmp_path/'projection'
    (source/'openspec/specs').mkdir(parents=True);projection.mkdir()
    (source/'openspec/specs/a.md').write_text('trusted but wrong workspace')
    check={'inputs':['openspec/specs']}
    assert fingerprint(source,check)!=fingerprint(projection,check,source_root=source)


def test_directory_order_and_workspace_location_do_not_affect_hash(tmp_path):
    first,second=tmp_path/'a',tmp_path/'b';first.mkdir();second.mkdir()
    for name in ['z','a']:(first/name).write_text(name)
    for name in ['a','z']:(second/name).write_text(name)
    assert input_bytes(tmp_path,{},'a')==input_bytes(tmp_path,{},'b')


def test_source_inputs_validate_the_selected_root_not_an_unused_projection(tmp_path):
    source, projection, outside = (tmp_path / name for name in ('source', 'projection', 'outside'))
    for path in (source / 'src', projection, outside): path.mkdir(parents=True)
    (outside / 'a.py').write_text('outside')
    (projection / 'src').symlink_to(outside, target_is_directory=True)
    target = source / 'src/a.py'
    target.write_text('authorized source')
    assert input_bytes(projection, {}, 'src/a.py', source_root=source) == b'authorized source'
    target.unlink()
    target.symlink_to(outside / 'a.py')
    with pytest.raises(ValueError):
        input_bytes(projection, {}, 'src/a.py', source_root=source)
