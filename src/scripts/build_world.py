from src.utils import world_data

# List of lists of dictionaries that can be passed to the constructor for defining
# the world tiles. Need to design these first
LOCATIONS = [
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

for group in LOCATIONS:
    for loc in group:
        warnings = world_data.create_location(**loc)
        for msg in warnings.messages:
            print("warning:", msg)
