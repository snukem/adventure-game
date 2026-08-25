"""CRUD for the tile-based world: locations and the loot/item catalog.

Data lives in data/world.json:
{
  "locations": {
    "<id>": {
      "name": str, "description": str,
      "x": int, "y": int,
      "area": str | null,
      "exits": {"<direction>": "<location_id>"},
      "loot": ["<item_id>", ...]
    }
  },
  "items": {
    "<id>": {
      "name": str, "description": str,
      "type": str, "category": str, "rarity": str,
      "value": int | float, "weight": int | float,
      "owner": str | null
    }
  }
}

Every item carries type/category/rarity -- there's no default for those, they must
be given explicitly. "owner" is the only field allowed to be null: it defaults to
null (unowned) for everything except Unique-rarity items, which must be created
with an explicit owner. The catalog only stores who currently owns an item as
authored; reassigning it when a player picks something up is the game engine's
job, not this module's.

x/y are the single global coordinate system -- there's no separate local
grid to keep in sync. A multi-tile place like a courtyard is several
location records that share an "area" tag (e.g. "castle_courtyard"), each
with its own global x/y and its own exits, conventionally id'd
"<area>_<x>_<y>" (e.g. "castle_courtyard_12_7"). No two locations may
share the same (x, y).

Forward references (an exit or loot id pointing at something you haven't
created yet) are allowed -- that's normal while sketching out a map -- but
every write is checked for structural correctness (required fields, right
types, no duplicate ids, no overlapping coordinates) and dangling
references are reported back as warnings so you can fix them without
losing work.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .storage import DATA_DIR, ValidationError, load_json, save_json

WORLD_PATH = DATA_DIR / "world.json"

VALID_DIRECTIONS = {"north", "south", "east", "west", "up", "down", "in", "out"}

VALID_ITEM_CATEGORIES = {"Weapon", "Armor", "Clothing", "Jewelry", "Food", "Drink", "Tool"}

VALID_RARITIES = {"Common", "Uncommon", "Rare", "Unique"}


def _empty_world() -> dict[str, Any]:
    return {"locations": {}, "items": {}}


def _load() -> dict[str, Any]:
    data = load_json(WORLD_PATH, _empty_world())
    data.setdefault("locations", {})
    data.setdefault("items", {})
    return data


def _save(data: dict[str, Any]) -> None:
    save_json(WORLD_PATH, data)


@dataclass
class Warnings:
    messages: list[str] = field(default_factory=list)

    def add(self, message: str) -> None:
        self.messages.append(message)


def _validate_location(loc_id: str, loc: dict[str, Any]) -> None:
    if not loc_id or not isinstance(loc_id, str):
        raise ValidationError("Location id must be a non-empty string.")
    if "name" not in loc or not isinstance(loc["name"], str) or not loc["name"]:
        raise ValidationError(f"Location '{loc_id}' requires a non-empty 'name'.")
    for coord in ("x", "y"):
        if coord in loc and loc[coord] is not None and not isinstance(loc[coord], int):
            raise ValidationError(f"Location '{loc_id}' field '{coord}' must be an int.")
    if loc.get("area") is not None and not isinstance(loc["area"], str):
        raise ValidationError(f"Location '{loc_id}' field 'area' must be a string or null.")
    exits = loc.get("exits", {})
    if not isinstance(exits, dict):
        raise ValidationError(f"Location '{loc_id}' field 'exits' must be a dict.")
    for direction, target in exits.items():
        if direction not in VALID_DIRECTIONS:
            raise ValidationError(
                f"Location '{loc_id}' has invalid exit direction '{direction}'. "
                f"Valid: {sorted(VALID_DIRECTIONS)}"
            )
        if not isinstance(target, str) or not target:
            raise ValidationError(
                f"Location '{loc_id}' exit '{direction}' must point to a location id string."
            )
    loot = loc.get("loot", [])
    if not isinstance(loot, list) or not all(isinstance(i, str) for i in loot):
        raise ValidationError(f"Location '{loc_id}' field 'loot' must be a list of item ids.")


def _validate_item(item_id: str, item: dict[str, Any]) -> None:
    if not item_id or not isinstance(item_id, str):
        raise ValidationError("Item id must be a non-empty string.")
    if "name" not in item or not isinstance(item["name"], str) or not item["name"]:
        raise ValidationError(f"Item '{item_id}' requires a non-empty 'name'.")
    if "type" not in item or not isinstance(item["type"], str) or not item["type"]:
        raise ValidationError(f"Item '{item_id}' requires a non-empty 'type'.")
    if item.get("category") not in VALID_ITEM_CATEGORIES:
        raise ValidationError(
            f"Item '{item_id}' field 'category' must be one of {sorted(VALID_ITEM_CATEGORIES)}."
        )
    if item.get("rarity") not in VALID_RARITIES:
        raise ValidationError(
            f"Item '{item_id}' field 'rarity' must be one of {sorted(VALID_RARITIES)}."
        )
    owner = item.get("owner")
    if owner is not None and not isinstance(owner, str):
        raise ValidationError(f"Item '{item_id}' field 'owner' must be a string or null.")
    if item["rarity"] == "Unique" and owner is None:
        raise ValidationError(f"Item '{item_id}' is Unique and requires a non-null 'owner'.")
    if "value" in item and item["value"] is not None and not isinstance(item["value"], (int, float)):
        raise ValidationError(f"Item '{item_id}' field 'value' must be numeric.")
    if "weight" in item and item["weight"] is not None and not isinstance(item["weight"], (int, float)):
        raise ValidationError(f"Item '{item_id}' field 'weight' must be numeric.")


def _check_coordinate_collision(data: dict[str, Any], loc_id: str, x: int | None, y: int | None) -> None:
    if x is None or y is None:
        return
    for other_id, other in data["locations"].items():
        if other_id != loc_id and other.get("x") == x and other.get("y") == y:
            raise ValidationError(
                f"Location '{loc_id}' shares coordinates ({x}, {y}) with existing location '{other_id}'."
            )


def check_dangling_references(data: dict[str, Any] | None = None) -> Warnings:
    """Report exits/loot that point at locations or items that don't exist yet."""
    data = data if data is not None else _load()
    warnings = Warnings()
    locations = data["locations"]
    items = data["items"]
    for loc_id, loc in locations.items():
        for direction, target in loc.get("exits", {}).items():
            if target not in locations:
                warnings.add(f"Location '{loc_id}' exit '{direction}' -> unknown location '{target}'.")
        for item_id in loc.get("loot", []):
            if item_id not in items:
                warnings.add(f"Location '{loc_id}' loot references unknown item '{item_id}'.")
    return warnings


# ---- Locations ---------------------------------------------------------

def create_location(
    location_id: str,
    name: str,
    description: str = "",
    x: int | None = None,
    y: int | None = None,
    area: str | None = None,
    exits: dict[str, str] | None = None,
    loot: list[str] | None = None,
) -> Warnings:
    data = _load()
    if location_id in data["locations"]:
        raise ValidationError(f"Location '{location_id}' already exists. Use update_location instead.")
    loc = {
        "name": name,
        "description": description,
        "x": x,
        "y": y,
        "area": area,
        "exits": exits or {},
        "loot": loot or [],
    }
    _validate_location(location_id, loc)
    _check_coordinate_collision(data, location_id, x, y)
    data["locations"][location_id] = loc
    _save(data)
    return check_dangling_references(data)


def update_location(location_id: str, **fields: Any) -> Warnings:
    data = _load()
    if location_id not in data["locations"]:
        raise ValidationError(f"Location '{location_id}' does not exist.")
    loc = {**data["locations"][location_id], **fields}
    _validate_location(location_id, loc)
    _check_coordinate_collision(data, location_id, loc.get("x"), loc.get("y"))
    data["locations"][location_id] = loc
    _save(data)
    return check_dangling_references(data)


def delete_location(location_id: str, force: bool = False) -> Warnings:
    data = _load()
    if location_id not in data["locations"]:
        raise ValidationError(f"Location '{location_id}' does not exist.")

    referencing = [
        f"'{lid}' exit -> '{location_id}'"
        for lid, loc in data["locations"].items()
        if location_id in loc.get("exits", {}).values() and lid != location_id
    ]
    if referencing and not force:
        raise ValidationError(
            f"Location '{location_id}' is referenced by: {', '.join(referencing)}. "
            "Pass force=True to delete anyway (those exits will dangle)."
        )

    del data["locations"][location_id]
    _save(data)
    return check_dangling_references(data)


def get_location(location_id: str) -> dict[str, Any] | None:
    return _load()["locations"].get(location_id)


def list_locations() -> dict[str, Any]:
    return _load()["locations"]


def list_locations_by_area(area: str) -> dict[str, Any]:
    return {lid: loc for lid, loc in _load()["locations"].items() if loc.get("area") == area}


# ---- Items / Loot -------------------------------------------------------

def create_item(
    item_id: str,
    name: str,
    type: str,
    category: str,
    rarity: str,
    value: float = 0,
    weight: float = 0,
    owner: str | None = None,
    description: str = "",
) -> Warnings:
    data = _load()
    if item_id in data["items"]:
        raise ValidationError(f"Item '{item_id}' already exists. Use update_item instead.")
    item = {
        "name": name,
        "description": description,
        "type": type,
        "category": category,
        "rarity": rarity,
        "value": value,
        "weight": weight,
        "owner": owner,
    }
    _validate_item(item_id, item)
    data["items"][item_id] = item
    _save(data)
    return check_dangling_references(data)


def update_item(item_id: str, **fields: Any) -> Warnings:
    data = _load()
    if item_id not in data["items"]:
        raise ValidationError(f"Item '{item_id}' does not exist.")
    item = {**data["items"][item_id], **fields}
    _validate_item(item_id, item)
    data["items"][item_id] = item
    _save(data)
    return check_dangling_references(data)


def delete_item(item_id: str, force: bool = False) -> Warnings:
    data = _load()
    if item_id not in data["items"]:
        raise ValidationError(f"Item '{item_id}' does not exist.")

    referencing = [lid for lid, loc in data["locations"].items() if item_id in loc.get("loot", [])]
    if referencing and not force:
        raise ValidationError(
            f"Item '{item_id}' is referenced as loot in: {', '.join(referencing)}. "
            "Pass force=True to delete anyway (those references will dangle)."
        )

    del data["items"][item_id]
    _save(data)
    return check_dangling_references(data)


def get_item(item_id: str) -> dict[str, Any] | None:
    return _load()["items"].get(item_id)


def list_items() -> dict[str, Any]:
    return _load()["items"]
