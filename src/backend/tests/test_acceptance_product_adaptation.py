"""Regression for real-product integration failures found by isolated acceptance."""
from types import SimpleNamespace
import pytest
from app.db import session
from app.core.config import ConfigurationError


def test_mysql_initialization_reuses_only_identical_index(monkeypatch):
    connection=SimpleNamespace(dialect=SimpleNamespace(name='mysql'))
    indexes=[{'name':'ix_admin_users_role','column_names':['role'],'unique':False}]
    monkeypatch.setattr(session,'inspect',lambda _:SimpleNamespace(get_indexes=lambda _:indexes))
    statement='CREATE INDEX ix_admin_users_role ON admin_users (role)'
    assert session._existing_mysql_index(connection,statement)
    indexes[0]['column_names']=['status']
    with pytest.raises(ConfigurationError,match='索引定义不一致'):
        session._existing_mysql_index(connection,statement)
    indexes.clear()
    assert not session._existing_mysql_index(connection,statement)


def test_sqlite_initialization_retains_native_if_not_exists():
    connection=SimpleNamespace(dialect=SimpleNamespace(name='sqlite'))
    assert not session._existing_mysql_index(connection,'CREATE INDEX IF NOT EXISTS ix_admin_users_role ON admin_users (role)')


def test_mysql_time_storage_and_wire_response_remain_utc(monkeypatch):
    from datetime import datetime, UTC
    from app.db.time_values import storage_time,row_times
    monkeypatch.setattr('app.core.config.settings',SimpleNamespace(database_type='mysql'))
    assert storage_time('2026-10-30T10:00:00+08:00')=='2026-10-30 02:00:00'
    assert row_times({'expires_at':datetime(2026,10,30,2),'name':'unchanged'})=={'expires_at':'2026-10-30T02:00:00Z','name':'unchanged'}
    monkeypatch.setattr('app.core.config.settings',SimpleNamespace(database_type='sqlite'))
    assert storage_time('2026-10-30T02:00:00Z')=='2026-10-30T02:00:00Z'
