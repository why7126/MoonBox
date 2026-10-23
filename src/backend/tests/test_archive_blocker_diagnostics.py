from app.chat.api import _chat_error_data
from app.chat.service import ChatError


def test_archive_diagnostics_are_bounded_and_visible():
    valid = dict(type='change', id='fix-example', status='archive_requirement_conflict',
                 message='原条文兼容证明未通过', action_hint='核验原约束与新增场景', visible=True)
    hidden = {**valid, 'visible': False}
    private = {**valid, 'message': '/Users/private/secret'}
    oversized = {**valid, 'message': 'a' * 1501}
    error = ChatError(2509, '未就绪', 409, kind='archive_blocked',
                      details={'archive_blockers': [valid, hidden, private, oversized, {'type': 'unknown'}]})
    data = _chat_error_data(error, 'request')
    assert data['archive_blockers'] == [valid]
    assert data['request_id'] == 'request'


def test_plain_errors_keep_existing_shape():
    assert _chat_error_data(ChatError(2509, '未就绪', 409), 'request') is None
