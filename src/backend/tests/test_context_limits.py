"""Exercise exact existing limits on the approved frozen governance copy."""
import os
from pathlib import Path

import pytest
from app.chat.service import ChatError
from app.governance import snapshot, read_snapshot
from test_context_resources import expand_to_limits


@pytest.mark.skipif(not os.environ.get('BUG_READ_SOURCE'), reason='explicit frozen sample')
def test_exact_limits_and_safe_rejection(tmp_path):
    source = snapshot.stable(Path(os.environ['BUG_READ_SOURCE']))
    root = tmp_path / 'source'
    for name, body in source.files.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)
    extra = expand_to_limits(root, source)
    try:
        result = read_snapshot.stable_read(root, 'limits')
        assert len(result.files) == 10000
        assert sum(map(len, result.files.values())) == 32 * 1024**2
        assert read_snapshot.stable_read(root, 'limits') == result
        overflow = root / 'docs/overflow.md'
        overflow.write_text('')
        with pytest.raises(ChatError) as error:
            read_snapshot.stable_read(root, 'limits')
        assert error.value.kind == 'source_unavailable'
        overflow.unlink()
        previous = extra[-1].read_bytes()
        extra[-1].write_bytes(previous + b'x')
        with pytest.raises(ChatError) as error:
            read_snapshot.stable_read(root, 'limits')
        assert error.value.kind == 'source_unavailable'
        extra[-1].write_bytes(previous)
        assert read_snapshot.stable_read(root, 'limits') == result
    finally:
        read_snapshot.clear()
