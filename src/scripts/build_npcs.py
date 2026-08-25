from src.utils import npc_data

# List of lists of dictionaries that can be passed to the constructor for defining
# the world's NPCs. Need to design these first
NPCS = [
    # Starting Dock
    [

    ],
    # Boat
    [

    ],
    # Town
    [

    ],
    # Ocean
    [

    ]
]

for group in NPCS:
    for npc in group:
        warnings = npc_data.create_npc(**npc)
        for msg in warnings.messages:
            print("warning:", msg)
