"""Command-line front end for safely building out game data during design.

Examples
--------
    python -m src.utils.cli location create --id forest_1 --name "Dark Forest" \\
        --x 0 --y 0 --exit north=forest_2 --loot rusty_sword

    python -m src.utils.cli location update --id forest_1 --exit south=forest_0

    python -m src.utils.cli item create --id rusty_sword --name "Rusty Sword" \\
        --value 5 --tag weapon --tag rusty

    python -m src.utils.cli npc create --id old_hermit --name "Old Hermit" \\
        --location forest_1 --dialogue "Who dares enter my forest?" --friendly

    python -m src.utils.cli trigger create --id find_sword --type on_enter \\
        --location forest_1 --action '{"give_item": "rusty_sword"}'

    python -m src.utils.cli location list
    python -m src.utils.cli location get --id forest_1
    python -m src.utils.cli location delete --id forest_1

Every write validates structure first (bad data is rejected before
touching disk) and prints any dangling-reference warnings (e.g. an exit
pointing at a location you haven't created yet) so you can keep iterating
without losing track of loose ends.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from . import npc_data, trigger_data, world_data
from .storage import ValidationError
from .world_data import Warnings


def _kv_pairs_to_dict(pairs: list[str] | None) -> dict[str, str]:
    result: dict[str, str] = {}
    for pair in pairs or []:
        if "=" not in pair:
            raise SystemExit(f"Expected key=value, got '{pair}'")
        key, _, value = pair.partition("=")
        result[key] = value
    return result


def _print_warnings(warnings: Warnings) -> None:
    for message in warnings.messages:
        print(f"  warning: {message}", file=sys.stderr)


def _print_record(record_id: str, record: dict[str, Any] | None) -> None:
    if record is None:
        print(f"'{record_id}' not found.", file=sys.stderr)
        raise SystemExit(1)
    print(json.dumps({record_id: record}, indent=2, sort_keys=True))


def _print_collection(collection: dict[str, Any]) -> None:
    print(json.dumps(collection, indent=2, sort_keys=True))


# ---- location -----------------------------------------------------------

def _cmd_location_create(args: argparse.Namespace) -> None:
    warnings = world_data.create_location(
        location_id=args.id,
        name=args.name,
        description=args.description or "",
        x=args.x,
        y=args.y,
        area=args.area,
        exits=_kv_pairs_to_dict(args.exit),
        loot=args.loot or [],
    )
    print(f"Created location '{args.id}'.")
    _print_warnings(warnings)


def _cmd_location_update(args: argparse.Namespace) -> None:
    fields: dict[str, Any] = {}
    if args.name is not None:
        fields["name"] = args.name
    if args.description is not None:
        fields["description"] = args.description
    if args.x is not None:
        fields["x"] = args.x
    if args.y is not None:
        fields["y"] = args.y
    if args.area is not None:
        fields["area"] = args.area
    if args.exit:
        fields["exits"] = _kv_pairs_to_dict(args.exit)
    if args.clear_exits:
        fields["exits"] = {}
    if args.loot:
        fields["loot"] = args.loot
    if args.clear_loot:
        fields["loot"] = []
    warnings = world_data.update_location(args.id, **fields)
    print(f"Updated location '{args.id}'.")
    _print_warnings(warnings)


def _cmd_location_delete(args: argparse.Namespace) -> None:
    warnings = world_data.delete_location(args.id, force=args.force)
    print(f"Deleted location '{args.id}'.")
    _print_warnings(warnings)


def _cmd_location_get(args: argparse.Namespace) -> None:
    _print_record(args.id, world_data.get_location(args.id))


def _cmd_location_list(args: argparse.Namespace) -> None:
    if args.area:
        _print_collection(world_data.list_locations_by_area(args.area))
    else:
        _print_collection(world_data.list_locations())


# ---- item -----------------------------------------------------------

def _cmd_item_create(args: argparse.Namespace) -> None:
    warnings = world_data.create_item(
        item_id=args.id,
        name=args.name,
        description=args.description or "",
        value=args.value or 0,
        tags=args.tag or [],
    )
    print(f"Created item '{args.id}'.")
    _print_warnings(warnings)


def _cmd_item_update(args: argparse.Namespace) -> None:
    fields: dict[str, Any] = {}
    if args.name is not None:
        fields["name"] = args.name
    if args.description is not None:
        fields["description"] = args.description
    if args.value is not None:
        fields["value"] = args.value
    if args.tag:
        fields["tags"] = args.tag
    warnings = world_data.update_item(args.id, **fields)
    print(f"Updated item '{args.id}'.")
    _print_warnings(warnings)


def _cmd_item_delete(args: argparse.Namespace) -> None:
    warnings = world_data.delete_item(args.id, force=args.force)
    print(f"Deleted item '{args.id}'.")
    _print_warnings(warnings)


def _cmd_item_get(args: argparse.Namespace) -> None:
    _print_record(args.id, world_data.get_item(args.id))


def _cmd_item_list(_args: argparse.Namespace) -> None:
    _print_collection(world_data.list_items())


# ---- npc -----------------------------------------------------------

def _cmd_npc_create(args: argparse.Namespace) -> None:
    warnings = npc_data.create_npc(
        npc_id=args.id,
        name=args.name,
        description=args.description or "",
        location_id=args.location,
        dialogue=args.dialogue or [],
        friendly=not args.hostile,
    )
    print(f"Created NPC '{args.id}'.")
    _print_warnings(warnings)


def _cmd_npc_update(args: argparse.Namespace) -> None:
    fields: dict[str, Any] = {}
    if args.name is not None:
        fields["name"] = args.name
    if args.description is not None:
        fields["description"] = args.description
    if args.location is not None:
        fields["location_id"] = args.location
    if args.clear_location:
        fields["location_id"] = None
    if args.dialogue:
        fields["dialogue"] = args.dialogue
    if args.hostile:
        fields["friendly"] = False
    if args.friendly:
        fields["friendly"] = True
    warnings = npc_data.update_npc(args.id, **fields)
    print(f"Updated NPC '{args.id}'.")
    _print_warnings(warnings)


def _cmd_npc_delete(args: argparse.Namespace) -> None:
    npc_data.delete_npc(args.id)
    print(f"Deleted NPC '{args.id}'.")


def _cmd_npc_get(args: argparse.Namespace) -> None:
    _print_record(args.id, npc_data.get_npc(args.id))


def _cmd_npc_list(_args: argparse.Namespace) -> None:
    _print_collection(npc_data.list_npcs())


# ---- trigger -----------------------------------------------------------

def _parse_json_arg(name: str, raw: str | None) -> dict[str, Any] | None:
    if raw is None:
        return None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"--{name} must be valid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise SystemExit(f"--{name} must be a JSON object.")
    return parsed


def _cmd_trigger_create(args: argparse.Namespace) -> None:
    warnings = trigger_data.create_trigger(
        trigger_id=args.id,
        type=args.type,
        location_id=args.location,
        condition=_parse_json_arg("condition", args.condition) or {},
        action=_parse_json_arg("action", args.action) or {},
        repeatable=args.repeatable,
    )
    print(f"Created trigger '{args.id}'.")
    _print_warnings(warnings)


def _cmd_trigger_update(args: argparse.Namespace) -> None:
    fields: dict[str, Any] = {}
    if args.type is not None:
        fields["type"] = args.type
    if args.location is not None:
        fields["location_id"] = args.location
    if args.clear_location:
        fields["location_id"] = None
    condition = _parse_json_arg("condition", args.condition)
    if condition is not None:
        fields["condition"] = condition
    action = _parse_json_arg("action", args.action)
    if action is not None:
        fields["action"] = action
    if args.repeatable:
        fields["repeatable"] = True
    if args.not_repeatable:
        fields["repeatable"] = False
    warnings = trigger_data.update_trigger(args.id, **fields)
    print(f"Updated trigger '{args.id}'.")
    _print_warnings(warnings)


def _cmd_trigger_delete(args: argparse.Namespace) -> None:
    trigger_data.delete_trigger(args.id)
    print(f"Deleted trigger '{args.id}'.")


def _cmd_trigger_get(args: argparse.Namespace) -> None:
    _print_record(args.id, trigger_data.get_trigger(args.id))


def _cmd_trigger_list(_args: argparse.Namespace) -> None:
    _print_collection(trigger_data.list_triggers())


# ---- argument parser -----------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m src.utils.cli",
        description="Create, modify, and delete adventure-game world data safely.",
    )
    top = parser.add_subparsers(dest="entity", required=True)

    # location
    location = top.add_parser("location", help="Manage tile locations.")
    loc_sub = location.add_subparsers(dest="action", required=True)

    p = loc_sub.add_parser("create")
    p.add_argument("--id", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--description")
    p.add_argument("--x", type=int)
    p.add_argument("--y", type=int)
    p.add_argument("--area", help="Groups multi-tile places, e.g. 'castle_courtyard'.")
    p.add_argument("--exit", action="append", metavar="DIRECTION=LOCATION_ID")
    p.add_argument("--loot", action="append", metavar="ITEM_ID")
    p.set_defaults(func=_cmd_location_create)

    p = loc_sub.add_parser("update")
    p.add_argument("--id", required=True)
    p.add_argument("--name")
    p.add_argument("--description")
    p.add_argument("--x", type=int)
    p.add_argument("--y", type=int)
    p.add_argument("--area")
    p.add_argument("--exit", action="append", metavar="DIRECTION=LOCATION_ID")
    p.add_argument("--clear-exits", action="store_true")
    p.add_argument("--loot", action="append", metavar="ITEM_ID")
    p.add_argument("--clear-loot", action="store_true")
    p.set_defaults(func=_cmd_location_update)

    p = loc_sub.add_parser("delete")
    p.add_argument("--id", required=True)
    p.add_argument("--force", action="store_true", help="Delete even if other locations exit into it.")
    p.set_defaults(func=_cmd_location_delete)

    p = loc_sub.add_parser("get")
    p.add_argument("--id", required=True)
    p.set_defaults(func=_cmd_location_get)

    p = loc_sub.add_parser("list")
    p.add_argument("--area", help="Only show locations tagged with this area.")
    p.set_defaults(func=_cmd_location_list)

    # item
    item = top.add_parser("item", help="Manage the loot/item catalog.")
    item_sub = item.add_subparsers(dest="action", required=True)

    p = item_sub.add_parser("create")
    p.add_argument("--id", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--description")
    p.add_argument("--value", type=float)
    p.add_argument("--tag", action="append")
    p.set_defaults(func=_cmd_item_create)

    p = item_sub.add_parser("update")
    p.add_argument("--id", required=True)
    p.add_argument("--name")
    p.add_argument("--description")
    p.add_argument("--value", type=float)
    p.add_argument("--tag", action="append")
    p.set_defaults(func=_cmd_item_update)

    p = item_sub.add_parser("delete")
    p.add_argument("--id", required=True)
    p.add_argument("--force", action="store_true", help="Delete even if a location still lists it as loot.")
    p.set_defaults(func=_cmd_item_delete)

    p = item_sub.add_parser("get")
    p.add_argument("--id", required=True)
    p.set_defaults(func=_cmd_item_get)

    p = item_sub.add_parser("list")
    p.set_defaults(func=_cmd_item_list)

    # npc
    npc = top.add_parser("npc", help="Manage NPCs.")
    npc_sub = npc.add_subparsers(dest="action", required=True)

    p = npc_sub.add_parser("create")
    p.add_argument("--id", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--description")
    p.add_argument("--location", dest="location", metavar="LOCATION_ID")
    p.add_argument("--dialogue", action="append")
    p.add_argument("--hostile", action="store_true")
    p.set_defaults(func=_cmd_npc_create)

    p = npc_sub.add_parser("update")
    p.add_argument("--id", required=True)
    p.add_argument("--name")
    p.add_argument("--description")
    p.add_argument("--location", dest="location", metavar="LOCATION_ID")
    p.add_argument("--clear-location", action="store_true")
    p.add_argument("--dialogue", action="append")
    p.add_argument("--friendly", action="store_true")
    p.add_argument("--hostile", action="store_true")
    p.set_defaults(func=_cmd_npc_update)

    p = npc_sub.add_parser("delete")
    p.add_argument("--id", required=True)
    p.set_defaults(func=_cmd_npc_delete)

    p = npc_sub.add_parser("get")
    p.add_argument("--id", required=True)
    p.set_defaults(func=_cmd_npc_get)

    p = npc_sub.add_parser("list")
    p.set_defaults(func=_cmd_npc_list)

    # trigger
    trigger = top.add_parser("trigger", help="Manage scripted triggers.")
    trigger_sub = trigger.add_subparsers(dest="action", required=True)

    p = trigger_sub.add_parser("create")
    p.add_argument("--id", required=True)
    p.add_argument("--type", required=True, help='e.g. "on_enter", "on_item_pickup", "on_talk"')
    p.add_argument("--location", dest="location", metavar="LOCATION_ID")
    p.add_argument("--condition", help="JSON object, e.g. '{\"has_item\": \"key\"}'")
    p.add_argument("--action", help="JSON object, e.g. '{\"give_item\": \"sword\"}'")
    p.add_argument("--repeatable", action="store_true")
    p.set_defaults(func=_cmd_trigger_create)

    p = trigger_sub.add_parser("update")
    p.add_argument("--id", required=True)
    p.add_argument("--type")
    p.add_argument("--location", dest="location", metavar="LOCATION_ID")
    p.add_argument("--clear-location", action="store_true")
    p.add_argument("--condition", help="JSON object")
    p.add_argument("--action", help="JSON object")
    p.add_argument("--repeatable", action="store_true")
    p.add_argument("--not-repeatable", action="store_true")
    p.set_defaults(func=_cmd_trigger_update)

    p = trigger_sub.add_parser("delete")
    p.add_argument("--id", required=True)
    p.set_defaults(func=_cmd_trigger_delete)

    p = trigger_sub.add_parser("get")
    p.add_argument("--id", required=True)
    p.set_defaults(func=_cmd_trigger_get)

    p = trigger_sub.add_parser("list")
    p.set_defaults(func=_cmd_trigger_list)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except ValidationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
