import pytest

from src.utils import world_data
from src.utils.storage import ValidationError


# ---- locations -----------------------------------------------------------

def test_create_location_persists_and_is_retrievable():
    world_data.create_location("forest_1", name="Dark Forest", x=0, y=0)
    loc = world_data.get_location("forest_1")
    assert loc["name"] == "Dark Forest"
    assert loc["x"] == 0 and loc["y"] == 0
    assert loc["exits"] == {}
    assert loc["loot"] == []


def test_create_location_duplicate_id_raises():
    world_data.create_location("forest_1", name="Dark Forest")
    with pytest.raises(ValidationError):
        world_data.create_location("forest_1", name="Different Forest")


def test_create_location_requires_name():
    with pytest.raises(ValidationError):
        world_data.create_location("forest_1", name="")


def test_create_location_rejects_invalid_exit_direction():
    with pytest.raises(ValidationError):
        world_data.create_location("forest_1", name="Dark Forest", exits={"northish": "forest_2"})


def test_create_location_rejects_non_string_exit_target():
    with pytest.raises(ValidationError):
        world_data.create_location("forest_1", name="Dark Forest", exits={"north": 123})


def test_create_location_rejects_non_string_area():
    with pytest.raises(ValidationError):
        world_data.create_location("forest_1", name="Dark Forest", area=123)


def test_create_location_area_defaults_to_none():
    world_data.create_location("forest_1", name="Dark Forest")
    assert world_data.get_location("forest_1")["area"] is None


def test_create_location_rejects_coordinate_collision():
    world_data.create_location("castle_courtyard_0_0", name="Courtyard NW", x=0, y=0)
    with pytest.raises(ValidationError):
        world_data.create_location("castle_courtyard_dup", name="Courtyard Dup", x=0, y=0)


def test_create_location_allows_same_coordinate_when_unset():
    world_data.create_location("a", name="A")
    world_data.create_location("b", name="B")  # both x=y=None, not a collision


def test_update_location_rejects_moving_onto_occupied_coordinate():
    world_data.create_location("a", name="A", x=0, y=0)
    world_data.create_location("b", name="B", x=1, y=0)
    with pytest.raises(ValidationError):
        world_data.update_location("b", x=0, y=0)


def test_update_location_allows_keeping_its_own_coordinate():
    world_data.create_location("a", name="A", x=0, y=0)
    world_data.update_location("a", description="Mossier now.")
    assert world_data.get_location("a")["x"] == 0


def test_list_locations_by_area_filters():
    world_data.create_location("castle_courtyard_0_0", name="Courtyard NW", x=0, y=0, area="castle_courtyard")
    world_data.create_location("castle_courtyard_1_0", name="Courtyard NE", x=1, y=0, area="castle_courtyard")
    world_data.create_location("forest_1", name="Dark Forest", area="forest")
    result = world_data.list_locations_by_area("castle_courtyard")
    assert set(result.keys()) == {"castle_courtyard_0_0", "castle_courtyard_1_0"}


def test_create_location_warns_on_dangling_exit():
    warnings = world_data.create_location("forest_1", name="Dark Forest", exits={"north": "forest_2"})
    assert any("forest_2" in msg for msg in warnings.messages)


def test_create_location_warns_on_dangling_loot():
    warnings = world_data.create_location("forest_1", name="Dark Forest", loot=["sword"])
    assert any("sword" in msg for msg in warnings.messages)


def test_create_location_no_warnings_when_references_resolve():
    world_data.create_location("forest_2", name="Deeper Forest")
    world_data.create_item("sword", name="Sword")
    warnings = world_data.create_location(
        "forest_1", name="Dark Forest", exits={"north": "forest_2"}, loot=["sword"]
    )
    assert warnings.messages == []


def test_update_location_merges_fields():
    world_data.create_location("forest_1", name="Dark Forest", x=0, y=0)
    world_data.update_location("forest_1", description="Now with more moss.")
    loc = world_data.get_location("forest_1")
    assert loc["name"] == "Dark Forest"
    assert loc["description"] == "Now with more moss."


def test_update_location_nonexistent_raises():
    with pytest.raises(ValidationError):
        world_data.update_location("nope", name="Nowhere")


def test_update_location_validates_merged_result():
    world_data.create_location("forest_1", name="Dark Forest")
    with pytest.raises(ValidationError):
        world_data.update_location("forest_1", name="")


def test_delete_location_removes_it():
    world_data.create_location("forest_1", name="Dark Forest")
    world_data.delete_location("forest_1")
    assert world_data.get_location("forest_1") is None


def test_delete_location_nonexistent_raises():
    with pytest.raises(ValidationError):
        world_data.delete_location("nope")


def test_delete_location_blocked_when_referenced_by_another_exit():
    world_data.create_location("forest_1", name="Dark Forest", exits={"north": "forest_2"})
    world_data.create_location("forest_2", name="Deeper Forest", exits={"south": "forest_1"})
    with pytest.raises(ValidationError):
        world_data.delete_location("forest_2")
    # Still there -- the blocked delete must not have partially applied.
    assert world_data.get_location("forest_2") is not None


def test_delete_location_force_overrides_reference_protection():
    world_data.create_location("forest_1", name="Dark Forest", exits={"north": "forest_2"})
    world_data.create_location("forest_2", name="Deeper Forest", exits={"south": "forest_1"})
    world_data.delete_location("forest_2", force=True)
    assert world_data.get_location("forest_2") is None


def test_list_locations_returns_all():
    world_data.create_location("a", name="A")
    world_data.create_location("b", name="B")
    assert set(world_data.list_locations().keys()) == {"a", "b"}


# ---- items / loot -----------------------------------------------------------

def test_create_item_persists_and_is_retrievable():
    world_data.create_item("sword", name="Sword", value=10, tags=["weapon"])
    item = world_data.get_item("sword")
    assert item["name"] == "Sword"
    assert item["value"] == 10
    assert item["tags"] == ["weapon"]


def test_create_item_duplicate_id_raises():
    world_data.create_item("sword", name="Sword")
    with pytest.raises(ValidationError):
        world_data.create_item("sword", name="Another Sword")


def test_create_item_requires_name():
    with pytest.raises(ValidationError):
        world_data.create_item("sword", name="")


def test_create_item_rejects_non_numeric_value():
    with pytest.raises(ValidationError):
        world_data.create_item("sword", name="Sword", value="a lot")


def test_update_item_merges_fields():
    world_data.create_item("sword", name="Sword", value=10)
    world_data.update_item("sword", value=15)
    item = world_data.get_item("sword")
    assert item["name"] == "Sword"
    assert item["value"] == 15


def test_update_item_nonexistent_raises():
    with pytest.raises(ValidationError):
        world_data.update_item("nope", name="Nothing")


def test_delete_item_removes_it():
    world_data.create_item("sword", name="Sword")
    world_data.delete_item("sword")
    assert world_data.get_item("sword") is None


def test_delete_item_blocked_when_referenced_as_loot():
    world_data.create_item("sword", name="Sword")
    world_data.create_location("forest_1", name="Dark Forest", loot=["sword"])
    with pytest.raises(ValidationError):
        world_data.delete_item("sword")
    assert world_data.get_item("sword") is not None


def test_delete_item_force_overrides_reference_protection():
    world_data.create_item("sword", name="Sword")
    world_data.create_location("forest_1", name="Dark Forest", loot=["sword"])
    world_data.delete_item("sword", force=True)
    assert world_data.get_item("sword") is None


def test_list_items_returns_all():
    world_data.create_item("sword", name="Sword")
    world_data.create_item("shield", name="Shield")
    assert set(world_data.list_items().keys()) == {"sword", "shield"}


def test_check_dangling_references_reports_both_kinds():
    world_data.create_location(
        "forest_1", name="Dark Forest", exits={"north": "forest_2"}, loot=["sword"]
    )
    warnings = world_data.check_dangling_references()
    assert len(warnings.messages) == 2
