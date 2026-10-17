import pytest

from app.chat.service import ChatError
from app.governance.candidates import validate


def test_unsupported_generate_action_is_rejected_before_validation():
    with pytest.raises(ChatError) as error:
        validate({}, {}, "REQ-0099-local-check", "issues/requirements/plan/REQ-0099-local-check", "unconnected-op")
    assert error.value.code == 2604
    assert "尚未接入产品写入链路" in error.value.message
