import json

import pytest

from src.utils import cli


def run(capsys, *args):
    exit_code = cli.main(list(args))
    captured = capsys.readouterr()
    return exit_code, captured.out, captured.err


def test_location_create_then_get(capsys):
    exit_code, out, _ = run(
        capsys, "location", "create", "--id", "forest_1", "--name", "Dark Forest", "--x", "0", "--y", "0"
    )
    assert exit_code == 0
    assert "Created location 'forest_1'" in out

    exit_code, out, _ = run(capsys, "location", "get", "--id", "forest_1")
    assert exit_code == 0
    data = json.loads(out)
    assert data["forest_1"]["name"] == "Dark Forest"


def test_location_create_with_exit_and_loot(capsys):
    run(capsys, "item", "create", "--id", "sword", "--name", "Sword")
    exit_code, out, _ = run(
        capsys,
        "location",
        "create",
        "--id",
        "forest_1",
        "--name",
        "Dark Forest",
        "--exit",
        "north=forest_2",
        "--loot",
        "sword",
    )
    assert exit_code == 0
    _, out, _ = run(capsys, "location", "get", "--id", "forest_1")
    data = json.loads(out)
    assert data["forest_1"]["exits"] == {"north": "forest_2"}
    assert data["forest_1"]["loot"] == ["sword"]


def test_location_create_warns_on_dangling_exit_to_stderr(capsys):
    _, _, err = run(
        capsys, "location", "create", "--id", "forest_1", "--name", "Dark Forest", "--exit", "north=forest_2"
    )
    assert "forest_2" in err


def test_location_create_duplicate_returns_error_exit_code(capsys):
    run(capsys, "location", "create", "--id", "forest_1", "--name", "Dark Forest")
    exit_code, out, err = run(capsys, "location", "create", "--id", "forest_1", "--name", "Again")
    assert exit_code == 1
    assert "error:" in err


def test_location_get_missing_exits_nonzero(capsys):
    with pytest.raises(SystemExit) as excinfo:
        run(capsys, "location", "get", "--id", "nope")
    assert excinfo.value.code == 1


def test_location_delete_blocked_without_force(capsys):
    run(capsys, "location", "create", "--id", "a", "--name", "A", "--exit", "north=b")
    run(capsys, "location", "create", "--id", "b", "--name", "B", "--exit", "south=a")
    exit_code, _, err = run(capsys, "location", "delete", "--id", "b")
    assert exit_code == 1
    assert "force" in err


def test_location_delete_with_force_succeeds(capsys):
    run(capsys, "location", "create", "--id", "a", "--name", "A", "--exit", "north=b")
    run(capsys, "location", "create", "--id", "b", "--name", "B", "--exit", "south=a")
    exit_code, out, _ = run(capsys, "location", "delete", "--id", "b", "--force")
    assert exit_code == 0
    assert "Deleted location 'b'" in out


def test_location_list_shows_all_created(capsys):
    run(capsys, "location", "create", "--id", "a", "--name", "A")
    run(capsys, "location", "create", "--id", "b", "--name", "B")
    exit_code, out, _ = run(capsys, "location", "list")
    data = json.loads(out)
    assert set(data.keys()) == {"a", "b"}


def test_location_list_filters_by_area(capsys):
    run(capsys, "location", "create", "--id", "castle_courtyard_0_0", "--name", "Courtyard NW",
        "--x", "0", "--y", "0", "--area", "castle_courtyard")
    run(capsys, "location", "create", "--id", "castle_courtyard_1_0", "--name", "Courtyard NE",
        "--x", "1", "--y", "0", "--area", "castle_courtyard")
    run(capsys, "location", "create", "--id", "forest_1", "--name", "Dark Forest", "--area", "forest")

    _, out, _ = run(capsys, "location", "list", "--area", "castle_courtyard")
    data = json.loads(out)
    assert set(data.keys()) == {"castle_courtyard_0_0", "castle_courtyard_1_0"}


def test_location_create_rejects_coordinate_collision(capsys):
    run(capsys, "location", "create", "--id", "a", "--name", "A", "--x", "0", "--y", "0")
    exit_code, _, err = run(capsys, "location", "create", "--id", "b", "--name", "B", "--x", "0", "--y", "0")
    assert exit_code == 1
    assert "coordinates" in err


def test_item_create_then_list(capsys):
    run(capsys, "item", "create", "--id", "sword", "--name", "Sword", "--value", "5", "--tag", "weapon")
    exit_code, out, _ = run(capsys, "item", "list")
    data = json.loads(out)
    assert data["sword"]["value"] == 5.0
    assert data["sword"]["tags"] == ["weapon"]


def test_npc_create_defaults_to_friendly(capsys):
    run(capsys, "npc", "create", "--id", "hermit", "--name", "Old Hermit")
    _, out, _ = run(capsys, "npc", "get", "--id", "hermit")
    data = json.loads(out)
    assert data["hermit"]["friendly"] is True


def test_npc_create_hostile_flag(capsys):
    run(capsys, "npc", "create", "--id", "bandit", "--name", "Bandit", "--hostile")
    _, out, _ = run(capsys, "npc", "get", "--id", "bandit")
    data = json.loads(out)
    assert data["bandit"]["friendly"] is False


def test_npc_delete(capsys):
    run(capsys, "npc", "create", "--id", "hermit", "--name", "Old Hermit")
    exit_code, out, _ = run(capsys, "npc", "delete", "--id", "hermit")
    assert exit_code == 0
    assert "Deleted NPC 'hermit'" in out


def test_trigger_create_with_json_action(capsys):
    exit_code, out, _ = run(
        capsys,
        "trigger",
        "create",
        "--id",
        "find_sword",
        "--type",
        "on_enter",
        "--action",
        '{"give_item": "sword"}',
    )
    assert exit_code == 0
    _, out, _ = run(capsys, "trigger", "get", "--id", "find_sword")
    data = json.loads(out)
    assert data["find_sword"]["action"] == {"give_item": "sword"}


def test_trigger_create_with_invalid_json_exits_nonzero(capsys):
    with pytest.raises(SystemExit):
        run(capsys, "trigger", "create", "--id", "bad", "--type", "on_enter", "--action", "{not json}")


def test_kv_pair_missing_equals_sign_exits(capsys):
    with pytest.raises(SystemExit):
        run(capsys, "location", "create", "--id", "a", "--name", "A", "--exit", "north-forest_2")
