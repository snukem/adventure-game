import pytest

from src.utils import trigger_data, world_data
from src.utils.storage import ValidationError


def test_create_trigger_persists_and_is_retrievable():
    trigger_data.create_trigger(
        "find_sword", type="on_enter", action={"give_item": "sword"}, repeatable=False
    )
    trigger = trigger_data.get_trigger("find_sword")
    assert trigger["type"] == "on_enter"
    assert trigger["action"] == {"give_item": "sword"}
    assert trigger["condition"] == {}
    assert trigger["repeatable"] is False


def test_create_trigger_duplicate_id_raises():
    trigger_data.create_trigger("find_sword", type="on_enter")
    with pytest.raises(ValidationError):
        trigger_data.create_trigger("find_sword", type="on_talk")


def test_create_trigger_requires_type():
    with pytest.raises(ValidationError):
        trigger_data.create_trigger("find_sword", type="")


def test_create_trigger_rejects_non_string_location_id():
    with pytest.raises(ValidationError):
        trigger_data.create_trigger("find_sword", type="on_enter", location_id=123)


def test_create_trigger_rejects_non_dict_condition():
    with pytest.raises(ValidationError):
        trigger_data.create_trigger("find_sword", type="on_enter", condition="has_key")


def test_create_trigger_rejects_non_dict_action():
    with pytest.raises(ValidationError):
        trigger_data.create_trigger("find_sword", type="on_enter", action="give sword")


def test_create_trigger_rejects_non_bool_repeatable():
    with pytest.raises(ValidationError):
        trigger_data.create_trigger("find_sword", type="on_enter", repeatable="yes")


def test_create_trigger_warns_on_dangling_location():
    warnings = trigger_data.create_trigger("find_sword", type="on_enter", location_id="forest_1")
    assert any("forest_1" in msg for msg in warnings.messages)


def test_create_trigger_no_warning_when_location_exists():
    world_data.create_location("forest_1", name="Dark Forest")
    warnings = trigger_data.create_trigger("find_sword", type="on_enter", location_id="forest_1")
    assert warnings.messages == []


def test_create_trigger_no_warning_when_location_bound_is_none():
    warnings = trigger_data.create_trigger("find_sword", type="on_enter")
    assert warnings.messages == []


def test_update_trigger_merges_fields():
    trigger_data.create_trigger("find_sword", type="on_enter", repeatable=False)
    trigger_data.update_trigger("find_sword", repeatable=True)
    trigger = trigger_data.get_trigger("find_sword")
    assert trigger["type"] == "on_enter"
    assert trigger["repeatable"] is True


def test_update_trigger_nonexistent_raises():
    with pytest.raises(ValidationError):
        trigger_data.update_trigger("nope", type="on_enter")


def test_delete_trigger_removes_it():
    trigger_data.create_trigger("find_sword", type="on_enter")
    trigger_data.delete_trigger("find_sword")
    assert trigger_data.get_trigger("find_sword") is None


def test_delete_trigger_nonexistent_raises():
    with pytest.raises(ValidationError):
        trigger_data.delete_trigger("nope")


def test_list_triggers_returns_all():
    trigger_data.create_trigger("a", type="on_enter")
    trigger_data.create_trigger("b", type="on_talk")
    assert set(trigger_data.list_triggers().keys()) == {"a", "b"}
