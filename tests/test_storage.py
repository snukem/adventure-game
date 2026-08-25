import json

import pytest

from src.utils import storage


def test_load_json_returns_default_when_missing(isolated_data_dir):
    path = isolated_data_dir / "missing.json"
    assert storage.load_json(path, {"default": True}) == {"default": True}


def test_save_then_load_roundtrip(isolated_data_dir):
    path = isolated_data_dir / "thing.json"
    storage.save_json(path, {"a": 1, "b": [1, 2, 3]})
    assert storage.load_json(path, None) == {"a": 1, "b": [1, 2, 3]}


def test_save_json_creates_parent_directories(tmp_path):
    path = tmp_path / "nested" / "dir" / "thing.json"
    storage.save_json(path, {"x": 1})
    assert path.exists()


def test_save_json_leaves_no_temp_files_behind(isolated_data_dir):
    path = isolated_data_dir / "thing.json"
    storage.save_json(path, {"a": 1})
    leftovers = list(isolated_data_dir.glob("*.tmp"))
    assert leftovers == []


def test_failed_write_does_not_corrupt_existing_file(isolated_data_dir, monkeypatch):
    path = isolated_data_dir / "thing.json"
    storage.save_json(path, {"good": "data"})

    def boom(*args, **kwargs):
        raise RuntimeError("simulated failure mid-write")

    monkeypatch.setattr(json, "dump", boom)
    with pytest.raises(RuntimeError):
        storage.save_json(path, {"bad": "data"})

    # Original file must be untouched, and no dangling temp file left over.
    assert storage.load_json(path, None) == {"good": "data"}
    assert list(isolated_data_dir.glob("*.tmp")) == []


def test_save_json_creates_a_backup_of_the_previous_version(isolated_data_dir):
    path = isolated_data_dir / "thing.json"
    storage.save_json(path, {"version": 1})
    storage.save_json(path, {"version": 2})

    backups = list(storage.BACKUP_DIR.glob("thing.*.bak.json"))
    assert len(backups) == 1
    assert json.loads(backups[0].read_text()) == {"version": 1}


def test_first_save_creates_no_backup(isolated_data_dir):
    path = isolated_data_dir / "thing.json"
    storage.save_json(path, {"version": 1})
    assert not storage.BACKUP_DIR.exists() or list(storage.BACKUP_DIR.iterdir()) == []


def test_backup_rotation_prunes_oldest(isolated_data_dir, monkeypatch):
    monkeypatch.setattr(storage, "MAX_BACKUPS_PER_FILE", 3)
    path = isolated_data_dir / "thing.json"
    for version in range(6):
        storage.save_json(path, {"version": version})

    backups = sorted(storage.BACKUP_DIR.glob("thing.*.bak.json"))
    assert len(backups) == 3
