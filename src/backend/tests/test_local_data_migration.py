import sqlite3

import pytest

from app.db.local_data_migration import CANONICAL, LEGACY, DATABASE_URL, cleanup_legacy, migrate, preflight, report, rollback


def database(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as db:
        db.execute('CREATE TABLE sample (value TEXT NOT NULL)')
        db.execute('INSERT INTO sample VALUES (?)', (value,))


def test_path_preflight_blocks_legacy_and_wrong_url(tmp_path):
    assert preflight(tmp_path, DATABASE_URL)['canonical_mount']
    with pytest.raises(ValueError, match='sqlite_database_url_not_canonical'):
        preflight(tmp_path, 'sqlite:////app/data/runtime/backend/sqlite/moonbox.db')
    database(tmp_path / LEGACY, 'legacy')
    with pytest.raises(ValueError, match='legacy_database_requires_offline_migration'):
        preflight(tmp_path, DATABASE_URL)


def test_different_databases_require_explicit_offline_source_and_allow_rollback(tmp_path):
    database(tmp_path / LEGACY, 'legacy')
    database(tmp_path / CANONICAL, 'canonical')
    assert report(tmp_path)['different']
    with pytest.raises(ValueError, match='stop_services_before_migration'):
        migrate(tmp_path, select='legacy', confirm_stopped=False)
    result = migrate(tmp_path, select='legacy', confirm_stopped=True)
    with sqlite3.connect(tmp_path / CANONICAL) as db:
        assert db.execute('SELECT value FROM sample').fetchone()[0] == 'legacy'
    assert result['legacy_preserved'] and result['canonical_preserved']
    with pytest.raises(ValueError, match='stop_services_before_cleanup'):
        cleanup_legacy(tmp_path, result['inventory_id'], confirm_stopped=False, verified=False)
    with pytest.raises(ValueError, match='verify_services_before_cleanup'):
        cleanup_legacy(tmp_path, result['inventory_id'], confirm_stopped=True, verified=False)
    assert cleanup_legacy(tmp_path, result['inventory_id'], confirm_stopped=True, verified=True)['legacy_removed']
    assert preflight(tmp_path, DATABASE_URL)['legacy_database'] is False
    assert rollback(tmp_path, result['inventory_id'], confirm_stopped=True)['rolled_back']
    with sqlite3.connect(tmp_path / CANONICAL) as db:
        assert db.execute('SELECT value FROM sample').fetchone()[0] == 'canonical'


def test_corrupt_legacy_is_not_migrated(tmp_path):
    source = tmp_path / LEGACY
    source.parent.mkdir(parents=True)
    source.write_text('not a database')
    with pytest.raises(sqlite3.DatabaseError):
        migrate(tmp_path, select='legacy', confirm_stopped=True)
    assert not (tmp_path / CANONICAL).exists()


def test_legacy_media_blocks_start_until_reviewed(tmp_path):
    media = tmp_path / 'data/runtime/backend/media/item.bin'
    media.parent.mkdir(parents=True)
    media.write_bytes(b'old-media')
    assert report(tmp_path)['legacy_media']['media']['files'] == 1
    with pytest.raises(ValueError, match='legacy_media_requires_review'):
        preflight(tmp_path, DATABASE_URL)


def test_equal_databases_still_need_explicit_source(tmp_path):
    database(tmp_path / LEGACY, 'same')
    (tmp_path / CANONICAL).parent.mkdir(parents=True)
    (tmp_path / CANONICAL).write_bytes((tmp_path / LEGACY).read_bytes())
    assert not report(tmp_path)['different']
    with pytest.raises(ValueError, match='explicit_source_required'):
        migrate(tmp_path, select='', confirm_stopped=True)


def test_backup_failure_does_not_switch_canonical(tmp_path, monkeypatch):
    database(tmp_path / LEGACY, 'legacy')
    database(tmp_path / CANONICAL, 'canonical')
    from app.db import local_data_migration as migration
    def disk_full(*_args):
        raise OSError('synthetic disk full')
    monkeypatch.setattr(migration, '_backup', disk_full)
    with pytest.raises(OSError, match='synthetic disk full'):
        migrate(tmp_path, select='legacy', confirm_stopped=True)
    with sqlite3.connect(tmp_path / CANONICAL) as db:
        assert db.execute('SELECT value FROM sample').fetchone()[0] == 'canonical'
