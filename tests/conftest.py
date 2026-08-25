import pytest

from src.utils import npc_data, storage, trigger_data, world_data


@pytest.fixture(autouse=True)
def isolated_data_dir(tmp_path, monkeypatch):
    """Point every data module at a throwaway directory for each test.

    The module-level *_PATH constants are plain Path objects computed once
    at import time, so patching storage.DATA_DIR alone wouldn't affect
    them -- each one is repointed explicitly.
    """
    data_dir = tmp_path / "data"
    monkeypatch.setattr(storage, "DATA_DIR", data_dir)
    monkeypatch.setattr(storage, "BACKUP_DIR", data_dir / ".backups")
    monkeypatch.setattr(world_data, "WORLD_PATH", data_dir / "world.json")
    monkeypatch.setattr(npc_data, "NPCS_PATH", data_dir / "npcs.json")
    monkeypatch.setattr(trigger_data, "TRIGGERS_PATH", data_dir / "triggers.json")
    yield data_dir
