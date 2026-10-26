import queue
import pytest
from app.chat.protocol_buffer import ByteQueue, validate_depth


def test_byte_backpressure_releases_after_consumer_and_has_bounded_timeout():
    buffer = ByteQueue(32)
    buffer.put({'text': 'x' * 64}, timeout=0)
    with pytest.raises(queue.Full): buffer.put({'text': 'y'}, timeout=0)
    assert buffer.get(timeout=0)['text'] == 'x' * 64
    assert buffer.bytes == 0
    buffer.put({'text': 'y'}, timeout=0)
    assert buffer.get(timeout=0)['text'] == 'y'
    with pytest.raises(queue.Empty): buffer.get(timeout=0)


def test_depth_guard_counts_structure_not_escaped_string_content():
    assert validate_depth(b'[' * 64 + b'0' + b']' * 64)
    assert not validate_depth(b'[' * 65 + b'0' + b']' * 65)
    assert validate_depth(b'{"text":"' + b'[' * 100 + b'\\\"still string"}')


def test_small_messages_respect_object_count_bound():
    import queue
    import pytest
    from app.chat.protocol_buffer import ByteQueue
    buffer = ByteQueue(maximum_items=2)
    buffer.put({}); buffer.put({})
    with pytest.raises(queue.Full): buffer.put({}, timeout=0)
    assert buffer.get() == {}
    buffer.put({}, timeout=0)
