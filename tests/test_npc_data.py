import pytest

from src.utils import npc_data, world_data
from src.utils.storage import ValidationError


def test_create_npc_persists_and_is_retrievable():
    npc_data.create_npc("hermit", name="Old Hermit", dialogue=["Who goes there?"])
    npc = npc_data.get_npc("hermit")
    assert npc["name"] == "Old Hermit"
    assert npc["dialogue"] == ["Who goes there?"]
    assert npc["friendly"] is True
    assert npc["location_id"] is None


def test_create_npc_duplicate_id_raises():
    npc_data.create_npc("hermit", name="Old Hermit")
    with pytest.raises(ValidationError):
        npc_data.create_npc("hermit", name="Another Hermit")


def test_create_npc_requires_name():
    with pytest.raises(ValidationError):
        npc_data.create_npc("hermit", name="")


def test_create_npc_rejects_non_string_location_id():
    with pytest.raises(ValidationError):
        npc_data.create_npc("hermit", name="Old Hermit", location_id=123)


def test_create_npc_rejects_non_list_dialogue():
    with pytest.raises(ValidationError):
        npc_data.create_npc("hermit", name="Old Hermit", dialogue="Hello there")


def test_create_npc_rejects_non_bool_friendly():
    with pytest.raises(ValidationError):
        npc_data.create_npc("hermit", name="Old Hermit", friendly="yes")


def test_create_npc_warns_on_dangling_location():
    warnings = npc_data.create_npc("hermit", name="Old Hermit", location_id="forest_1")
    assert any("forest_1" in msg for msg in warnings.messages)


def test_create_npc_no_warning_when_location_exists():
    world_data.create_location("forest_1", name="Dark Forest")
    warnings = npc_data.create_npc("hermit", name="Old Hermit", location_id="forest_1")
    assert warnings.messages == []


def test_create_npc_no_warning_when_unplaced():
    warnings = npc_data.create_npc("hermit", name="Old Hermit", location_id=None)
    assert warnings.messages == []


def test_update_npc_merges_fields():
    npc_data.create_npc("hermit", name="Old Hermit", friendly=True)
    npc_data.update_npc("hermit", friendly=False)
    npc = npc_data.get_npc("hermit")
    assert npc["name"] == "Old Hermit"
    assert npc["friendly"] is False


def test_update_npc_nonexistent_raises():
    with pytest.raises(ValidationError):
        npc_data.update_npc("nope", name="Nobody")


def test_delete_npc_removes_it():
    npc_data.create_npc("hermit", name="Old Hermit")
    npc_data.delete_npc("hermit")
    assert npc_data.get_npc("hermit") is None


def test_delete_npc_nonexistent_raises():
    with pytest.raises(ValidationError):
        npc_data.delete_npc("nope")


def test_list_npcs_returns_all():
    npc_data.create_npc("hermit", name="Old Hermit")
    npc_data.create_npc("guard", name="Guard")
    assert set(npc_data.list_npcs().keys()) == {"hermit", "guard"}
