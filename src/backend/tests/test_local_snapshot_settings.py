import pytest

from app.chat.settings import local_snapshot_limit
from app.chat.platform import fingerprint
from app.core.config import ConfigurationError, Settings


def test_snapshot_limit_default_zero_positive_and_invalid(monkeypatch):
    monkeypatch.delenv('MOONBOX_CHAT_LOCAL_SNAPSHOT_LIMIT', raising=False)
    assert local_snapshot_limit() == 2
    baseline = fingerprint()
    monkeypatch.setenv('MOONBOX_CHAT_LOCAL_SNAPSHOT_LIMIT', '0')
    assert local_snapshot_limit() == 0
    assert fingerprint() != baseline
    monkeypatch.setenv('MOONBOX_CHAT_LOCAL_SNAPSHOT_LIMIT', '3')
    assert local_snapshot_limit() == 3
    for value in ('', '-1', '1.5', 'two', ' 2', '+2'):
        monkeypatch.setenv('MOONBOX_CHAT_LOCAL_SNAPSHOT_LIMIT', value)
        with pytest.raises(ValueError, match='MOONBOX_CHAT_LOCAL_SNAPSHOT_LIMIT'):
            local_snapshot_limit()


def test_production_database_does_not_fall_back_to_sqlite():
    with pytest.raises(ConfigurationError):
        Settings(app_env='production', database_type='sqlite',
                 database_url='sqlite:////app/data/sqlite/moonbox.db').validate_database()
    with pytest.raises(ConfigurationError):
        Settings(app_env='production', database_type='mysql', mysql_database_url=None).validate_database()
