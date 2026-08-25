"""CRUD for NPCs.

Data lives in data/npcs.json:
{
  "npcs": {
    "<id>": {
      "name": str, "description": str,
      "location_id": str | null,
      "dialogue": [str],
      "friendly": bool
    }
  }
}

An NPC's location_id may point at a location that doesn't exist yet (or is
null, meaning "not placed"); that's reported as a warning, not blocked, so
you can create NPCs before you've built out where they live.
"""

from __future__ import annotations

from typing import Any

from .storage import DATA_DIR, ValidationError, load_json, save_json
from .world_data import Warnings, list_locations

NPCS_PATH = DATA_DIR / "npcs.json"


def _empty_npcs() -> dict[str, Any]:
    return {"npcs": {}}


def _load() -> dict[str, Any]:
    data = load_json(NPCS_PATH, _empty_npcs())
    data.setdefault("npcs", {})
    return data


def _save(data: dict[str, Any]) -> None:
    save_json(NPCS_PATH, data)


def _validate_npc(npc_id: str, npc: dict[str, Any]) -> None:
    if not npc_id or not isinstance(npc_id, str):
        raise ValidationError("NPC id must be a non-empty string.")
    if "name" not in npc or not isinstance(npc["name"], str) or not npc["name"]:
        raise ValidationError(f"NPC '{npc_id}' requires a non-empty 'name'.")
    if npc.get("location_id") is not None and not isinstance(npc["location_id"], str):
        raise ValidationError(f"NPC '{npc_id}' field 'location_id' must be a string or null.")
    dialogue = npc.get("dialogue", [])
    if not isinstance(dialogue, list) or not all(isinstance(d, str) for d in dialogue):
        raise ValidationError(f"NPC '{npc_id}' field 'dialogue' must be a list of strings.")
    if "friendly" in npc and not isinstance(npc["friendly"], bool):
        raise ValidationError(f"NPC '{npc_id}' field 'friendly' must be a bool.")


def check_dangling_references(data: dict[str, Any] | None = None) -> Warnings:
    data = data if data is not None else _load()
    locations = list_locations()
    warnings = Warnings()
    for npc_id, npc in data["npcs"].items():
        loc_id = npc.get("location_id")
        if loc_id is not None and loc_id not in locations:
            warnings.add(f"NPC '{npc_id}' location_id -> unknown location '{loc_id}'.")
    return warnings


def create_npc(
    npc_id: str,
    name: str,
    description: str = "",
    location_id: str | None = None,
    dialogue: list[str] | None = None,
    friendly: bool = True,
) -> Warnings:
    data = _load()
    if npc_id in data["npcs"]:
        raise ValidationError(f"NPC '{npc_id}' already exists. Use update_npc instead.")
    npc = {
        "name": name,
        "description": description,
        "location_id": location_id,
        "dialogue": dialogue or [],
        "friendly": friendly,
    }
    _validate_npc(npc_id, npc)
    data["npcs"][npc_id] = npc
    _save(data)
    return check_dangling_references(data)


def update_npc(npc_id: str, **fields: Any) -> Warnings:
    data = _load()
    if npc_id not in data["npcs"]:
        raise ValidationError(f"NPC '{npc_id}' does not exist.")
    npc = {**data["npcs"][npc_id], **fields}
    _validate_npc(npc_id, npc)
    data["npcs"][npc_id] = npc
    _save(data)
    return check_dangling_references(data)


def delete_npc(npc_id: str) -> None:
    data = _load()
    if npc_id not in data["npcs"]:
        raise ValidationError(f"NPC '{npc_id}' does not exist.")
    del data["npcs"][npc_id]
    _save(data)


def get_npc(npc_id: str) -> dict[str, Any] | None:
    return _load()["npcs"].get(npc_id)


def list_npcs() -> dict[str, Any]:
    return _load()["npcs"]
