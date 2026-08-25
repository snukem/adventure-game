"""CRUD for triggers (scripted world events).

Data lives in data/triggers.json:
{
  "triggers": {
    "<id>": {
      "type": str,               # e.g. "on_enter", "on_item_pickup", "on_talk"
      "location_id": str | null, # where the trigger fires, if location-bound
      "condition": {...},        # free-form, interpreted by the game engine
      "action": {...},           # free-form, interpreted by the game engine
      "repeatable": bool
    }
  }
}

'condition' and 'action' are intentionally free-form dicts -- the specific
keys they need depend on your game engine's trigger-handling code, which
doesn't exist yet. This module only enforces the structural envelope
(type/location_id/repeatable) and warns about a dangling location_id.
"""

from __future__ import annotations

from typing import Any

from .storage import DATA_DIR, ValidationError, load_json, save_json
from .world_data import Warnings, list_locations

TRIGGERS_PATH = DATA_DIR / "triggers.json"


def _empty_triggers() -> dict[str, Any]:
    return {"triggers": {}}


def _load() -> dict[str, Any]:
    data = load_json(TRIGGERS_PATH, _empty_triggers())
    data.setdefault("triggers", {})
    return data


def _save(data: dict[str, Any]) -> None:
    save_json(TRIGGERS_PATH, data)


def _validate_trigger(trigger_id: str, trigger: dict[str, Any]) -> None:
    if not trigger_id or not isinstance(trigger_id, str):
        raise ValidationError("Trigger id must be a non-empty string.")
    if not trigger.get("type") or not isinstance(trigger["type"], str):
        raise ValidationError(f"Trigger '{trigger_id}' requires a non-empty 'type' string.")
    if trigger.get("location_id") is not None and not isinstance(trigger["location_id"], str):
        raise ValidationError(f"Trigger '{trigger_id}' field 'location_id' must be a string or null.")
    for field_name in ("condition", "action"):
        if field_name in trigger and not isinstance(trigger[field_name], dict):
            raise ValidationError(f"Trigger '{trigger_id}' field '{field_name}' must be a dict.")
    if "repeatable" in trigger and not isinstance(trigger["repeatable"], bool):
        raise ValidationError(f"Trigger '{trigger_id}' field 'repeatable' must be a bool.")


def check_dangling_references(data: dict[str, Any] | None = None) -> Warnings:
    data = data if data is not None else _load()
    locations = list_locations()
    warnings = Warnings()
    for trigger_id, trigger in data["triggers"].items():
        loc_id = trigger.get("location_id")
        if loc_id is not None and loc_id not in locations:
            warnings.add(f"Trigger '{trigger_id}' location_id -> unknown location '{loc_id}'.")
    return warnings


def create_trigger(
    trigger_id: str,
    type: str,
    location_id: str | None = None,
    condition: dict[str, Any] | None = None,
    action: dict[str, Any] | None = None,
    repeatable: bool = False,
) -> Warnings:
    data = _load()
    if trigger_id in data["triggers"]:
        raise ValidationError(f"Trigger '{trigger_id}' already exists. Use update_trigger instead.")
    trigger = {
        "type": type,
        "location_id": location_id,
        "condition": condition or {},
        "action": action or {},
        "repeatable": repeatable,
    }
    _validate_trigger(trigger_id, trigger)
    data["triggers"][trigger_id] = trigger
    _save(data)
    return check_dangling_references(data)


def update_trigger(trigger_id: str, **fields: Any) -> Warnings:
    data = _load()
    if trigger_id not in data["triggers"]:
        raise ValidationError(f"Trigger '{trigger_id}' does not exist.")
    trigger = {**data["triggers"][trigger_id], **fields}
    _validate_trigger(trigger_id, trigger)
    data["triggers"][trigger_id] = trigger
    _save(data)
    return check_dangling_references(data)


def delete_trigger(trigger_id: str) -> None:
    data = _load()
    if trigger_id not in data["triggers"]:
        raise ValidationError(f"Trigger '{trigger_id}' does not exist.")
    del data["triggers"][trigger_id]
    _save(data)


def get_trigger(trigger_id: str) -> dict[str, Any] | None:
    return _load()["triggers"].get(trigger_id)


def list_triggers() -> dict[str, Any]:
    return _load()["triggers"]
