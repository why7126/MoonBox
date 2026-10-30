from uuid import uuid4
from app.moonbox_exec_server.git_view import prepare
from test_managed_worktree_git import repo, git


def test_linked_executor_view_has_no_peer_refs_or_objects(repo, tmp_path):
    source, managed = repo
    own = source.create(managed, str(uuid4()), source.head())
    peer = source.create(managed, str(uuid4()), source.head())
    (peer/'peer-secret.txt').write_text('synthetic-private-peer')
    git(peer, 'add', '.')
    git(peer, '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'peer')
    secret = git(peer, 'rev-parse', 'HEAD')
    runtime = tmp_path/'runtime'; runtime.mkdir()
    view, pointer = prepare(own, runtime)
    assert pointer.read_text() == 'gitdir: /git\n'
    assert git(own, '--git-dir='+str(view), '--work-tree='+str(own), 'rev-parse', 'HEAD') == source.head()
    assert git(own, '--git-dir='+str(view), '--work-tree='+str(own), 'for-each-ref', '--format=%(refname)') == 'refs/heads/workspace'
    import subprocess
    missing = subprocess.run(['git','--git-dir='+str(view),'cat-file','-e',secret],capture_output=True)
    assert missing.returncode != 0
    assert prepare(own, runtime) == (view, pointer)
