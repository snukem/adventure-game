# Adventure Game

A tile-based text adventure. Currently in the world-design phase: the game engine
(`src/game/`) hasn't been written yet, but the tooling to build and safely persist its
world, NPC, and trigger data (`src/utils/`) is ready to use.

## Setup

```bash
python3 -m venv gameenv
source gameenv/bin/activate
pip install -r requirements.txt
```

## Building the world

Game data lives as JSON under `data/` and is only ever touched through
`src/utils/`, which validates every write and keeps rolling backups. Build it up
from the command line as you design:

```bash
python -m src.utils.cli location create --id castle_courtyard_0_0 \
  --name "Castle Courtyard" --x 0 --y 0 --area castle_courtyard

python -m src.utils.cli item create --id rusty_key --name "Rusty Key"

python -m src.utils.cli npc create --id keep_warden --name "The Keep Warden" \
  --location castle_courtyard_0_0

python -m src.utils.cli trigger create --id warden_grants_key --type on_talk \
  --location castle_courtyard_0_0 --action '{"give_item": "rusty_key"}'

python -m src.utils.cli location list
```

Each entity (`location`, `item`, `npc`, `trigger`) supports `create`, `update`,
`delete`, `get`, and `list`. Run any subcommand with `-h` for its full flags.

## Layout

```
src/utils/   create/update/delete/get/list functions + CLI for world, item, NPC,
             and trigger data (storage.py, world_data.py, npc_data.py, trigger_data.py, cli.py)
src/game/    the game engine (not yet implemented)
data/        world.json, npcs.json, triggers.json + rolling backups in .backups/
tests/       pytest suite for src/utils/
```

## Testing

```bash
python -m pytest
```

Tests run against a throwaway data directory (see `tests/conftest.py`), never the
real `data/` folder.
