from src.utils import world_data

# List of lists of dictionaries that can be passed to the constructor for defining
# the item catalog, grouped by category. Material/quality prefix scales with
# rarity within each item type (e.g. Iron -> Silver -> Rune for weapons).
# Unique-rarity items are intentionally left out here -- add those by hand.
ITEMS = [
    # Weapon
    [
        dict(item_id="dagger_001", name="Dagger", type="Iron", category="Weapon", rarity="Common", value=1, weight=1),
        dict(item_id="dagger_002", name="Dagger", type="Silver", category="Weapon", rarity="Uncommon", value=3, weight=1),
        dict(item_id="dagger_003", name="Dagger", type="Rune", category="Weapon", rarity="Rare", value=10, weight=2),
        dict(item_id="dagger_004", name="Dagger", type="Ethereal", category="Weapon", rarity="Unique", value=100, weight=0, owner="Sir Mortimer"),

        dict(item_id="sword_001", name="Sword", type="Iron", category="Weapon", rarity="Common", value=4, weight=4),
        dict(item_id="sword_002", name="Sword", type="Silver", category="Weapon", rarity="Uncommon", value=12, weight=4),
        dict(item_id="sword_003", name="Sword", type="Rune", category="Weapon", rarity="Rare", value=40, weight=5),

        dict(item_id="axe_001", name="Axe", type="Iron", category="Weapon", rarity="Common", value=5, weight=6),
        dict(item_id="axe_002", name="Axe", type="Silver", category="Weapon", rarity="Uncommon", value=15, weight=6),
        dict(item_id="axe_003", name="Axe", type="Rune", category="Weapon", rarity="Rare", value=45, weight=7),

        dict(item_id="mace_001", name="Mace", type="Iron", category="Weapon", rarity="Common", value=4, weight=5),
        dict(item_id="mace_002", name="Mace", type="Silver", category="Weapon", rarity="Uncommon", value=13, weight=5),
        dict(item_id="mace_003", name="Mace", type="Rune", category="Weapon", rarity="Rare", value=42, weight=6),

        dict(item_id="bow_001", name="Bow", type="Ash", category="Weapon", rarity="Common", value=3, weight=2),
        dict(item_id="bow_002", name="Bow", type="Yew", category="Weapon", rarity="Uncommon", value=10, weight=2),
        dict(item_id="bow_003", name="Bow", type="Runic", category="Weapon", rarity="Rare", value=35, weight=3),
    ],
    # Armor
    [
        dict(item_id="armor_001", name="Armor", type="Leather", category="Armor", rarity="Common", value=5, weight=5),
        dict(item_id="armor_002", name="Armor", type="Silver", category="Armor", rarity="Uncommon", value=10, weight=10),
        dict(item_id="armor_003", name="Armor", type="Rune", category="Armor", rarity="Rare", value=40, weight=20),
        dict(item_id="armor_004", name="Armor", type="Ethereal", category="Armor", rarity="Unique", value=500, weight=0, owner="Cal'ad Feyn"),

        dict(item_id="armor_005", name="Helmet", type="Leather", category="Armor", rarity="Common", value=2, weight=1),
        dict(item_id="armor_006", name="Helmet", type="Silver", category="Armor", rarity="Uncommon", value=5, weight=2),
        dict(item_id="armor_007", name="Helmet", type="Rune", category="Armor", rarity="Rare", value=20, weight=5),
        dict(item_id="armor_008", name="Helmet", type="Ethereal", category="Armor", rarity="Unique", value=250, weight=0, owner="Deng"),

        dict(item_id="armor_009", name="Shield", type="Leather", category="Armor", rarity="Common", value=3, weight=3),
        dict(item_id="armor_010", name="Shield", type="Silver", category="Armor", rarity="Uncommon", value=10, weight=5),
        dict(item_id="armor_011", name="Shield", type="Rune", category="Armor", rarity="Rare", value=30, weight=15),
        dict(item_id="armor_012", name="Shield", type="Ethereal", category="Armor", rarity="Unique", value=400, weight=0, owner="Master Clint"),
    ],
    # Clothing
    [
        dict(item_id="clothing_001", name="Clothing", type="Rough", category="Clothing", rarity="Common", value=1, weight=2),
        dict(item_id="clothing_002", name="Clothing", type="Fine", category="Clothing", rarity="Uncommon", value=10, weight=3),
        dict(item_id="clothing_003", name="Clothing", type="Exquisite", category="Clothing", rarity="Rare", value=50, weight=3),
    ],
    # Jewelry
    [
        dict(item_id="ring_001", name="Ring", type="Copper", category="Jewelry", rarity="Common", value=5, weight=0),
        dict(item_id="ring_002", name="Ring", type="Silver", category="Jewelry", rarity="Uncommon", value=20, weight=0),
        dict(item_id="ring_003", name="Ring", type="Gold", category="Jewelry", rarity="Rare", value=75, weight=0),

        dict(item_id="necklace_001", name="Necklace", type="Copper", category="Jewelry", rarity="Common", value=8, weight=0),
        dict(item_id="necklace_002", name="Necklace", type="Silver", category="Jewelry", rarity="Uncommon", value=30, weight=0),
        dict(item_id="necklace_003", name="Necklace", type="Gold", category="Jewelry", rarity="Rare", value=100, weight=0),

        dict(item_id="bracelet_001", name="Bracelet", type="Copper", category="Jewelry", rarity="Common", value=6, weight=0),
        dict(item_id="bracelet_002", name="Bracelet", type="Silver", category="Jewelry", rarity="Uncommon", value=25, weight=0),
        dict(item_id="bracelet_003", name="Bracelet", type="Gold", category="Jewelry", rarity="Rare", value=85, weight=0),

        dict(item_id="amulet_001", name="Amulet", type="Copper", category="Jewelry", rarity="Common", value=10, weight=0),
        dict(item_id="amulet_002", name="Amulet", type="Silver", category="Jewelry", rarity="Uncommon", value=35, weight=0),
        dict(item_id="amulet_003", name="Amulet", type="Gold", category="Jewelry", rarity="Rare", value=120, weight=0),
    ],
    # Food
    [
        dict(item_id="bread_001", name="Bread", type="Stale", category="Food", rarity="Common", value=1, weight=1),
        dict(item_id="bread_002", name="Bread", type="Fresh", category="Food", rarity="Uncommon", value=3, weight=1),
        dict(item_id="bread_003", name="Bread", type="Gourmet", category="Food", rarity="Rare", value=8, weight=1),

        dict(item_id="cheese_001", name="Cheese", type="Stale", category="Food", rarity="Common", value=2, weight=1),
        dict(item_id="cheese_002", name="Cheese", type="Fresh", category="Food", rarity="Uncommon", value=5, weight=1),
        dict(item_id="cheese_003", name="Cheese", type="Gourmet", category="Food", rarity="Rare", value=12, weight=1),

        dict(item_id="stew_001", name="Stew", type="Stale", category="Food", rarity="Common", value=2, weight=1),
        dict(item_id="stew_002", name="Stew", type="Fresh", category="Food", rarity="Uncommon", value=6, weight=1),
        dict(item_id="stew_003", name="Stew", type="Gourmet", category="Food", rarity="Rare", value=15, weight=1),

        dict(item_id="meat_pie_001", name="Meat Pie", type="Stale", category="Food", rarity="Common", value=3, weight=1),
        dict(item_id="meat_pie_002", name="Meat Pie", type="Fresh", category="Food", rarity="Uncommon", value=8, weight=1),
        dict(item_id="meat_pie_003", name="Meat Pie", type="Gourmet", category="Food", rarity="Rare", value=18, weight=1),
    ],
    # Drink
    [
        dict(item_id="ale_001", name="Ale", type="Watered-Down", category="Drink", rarity="Common", value=1, weight=1),
        dict(item_id="ale_002", name="Ale", type="Fine", category="Drink", rarity="Uncommon", value=3, weight=1),
        dict(item_id="ale_003", name="Ale", type="Vintage", category="Drink", rarity="Rare", value=10, weight=1),

        dict(item_id="wine_001", name="Wine", type="Watered-Down", category="Drink", rarity="Common", value=2, weight=1),
        dict(item_id="wine_002", name="Wine", type="Fine", category="Drink", rarity="Uncommon", value=6, weight=1),
        dict(item_id="wine_003", name="Wine", type="Vintage", category="Drink", rarity="Rare", value=20, weight=1),

        dict(item_id="mead_001", name="Mead", type="Watered-Down", category="Drink", rarity="Common", value=2, weight=1),
        dict(item_id="mead_002", name="Mead", type="Fine", category="Drink", rarity="Uncommon", value=5, weight=1),
        dict(item_id="mead_003", name="Mead", type="Vintage", category="Drink", rarity="Rare", value=18, weight=1),

        dict(item_id="cider_001", name="Cider", type="Watered-Down", category="Drink", rarity="Common", value=1, weight=1),
        dict(item_id="cider_002", name="Cider", type="Fine", category="Drink", rarity="Uncommon", value=4, weight=1),
        dict(item_id="cider_003", name="Cider", type="Vintage", category="Drink", rarity="Rare", value=12, weight=1),
    ],
    # Tool
    [
        dict(item_id="rope_001", name="Rope", type="Worn", category="Tool", rarity="Common", value=1, weight=2),
        dict(item_id="rope_002", name="Rope", type="Sturdy", category="Tool", rarity="Uncommon", value=3, weight=2),
        dict(item_id="rope_003", name="Rope", type="Masterwork", category="Tool", rarity="Rare", value=10, weight=2),

        dict(item_id="torch_001", name="Torch", type="Worn", category="Tool", rarity="Common", value=1, weight=1),
        dict(item_id="torch_002", name="Torch", type="Sturdy", category="Tool", rarity="Uncommon", value=2, weight=1),
        dict(item_id="torch_003", name="Torch", type="Masterwork", category="Tool", rarity="Rare", value=6, weight=1),

        dict(item_id="lockpick_001", name="Lockpick", type="Worn", category="Tool", rarity="Common", value=2, weight=0),
        dict(item_id="lockpick_002", name="Lockpick", type="Sturdy", category="Tool", rarity="Uncommon", value=6, weight=0),
        dict(item_id="lockpick_003", name="Lockpick", type="Masterwork", category="Tool", rarity="Rare", value=18, weight=0),

        dict(item_id="shovel_001", name="Shovel", type="Worn", category="Tool", rarity="Common", value=2, weight=4),
        dict(item_id="shovel_002", name="Shovel", type="Sturdy", category="Tool", rarity="Uncommon", value=5, weight=4),
        dict(item_id="shovel_003", name="Shovel", type="Masterwork", category="Tool", rarity="Rare", value=15, weight=5),
    ],
]

for group in ITEMS:
    for item in group:
        warnings = world_data.create_item(**item)
        for msg in warnings.messages:
            print("warning:", msg)
