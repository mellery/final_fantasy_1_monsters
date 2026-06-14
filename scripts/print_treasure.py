"""Print treasure chest contents from Final Fantasy (USA).

The chest-contents table (lut_Treasure = $B100 in bank 0) is a flat array of
256 item ids at ROM offset 0x3110 (one byte per chest). Item ids 0x01-0x6b are
items/equipment and decode to verified names; ids 0x6c-0xaf are gold chests
(amount from the gold-name strings).

Verified against the mikesrpgcenter dungeon maps: e.g. Earth Cave chests
(1975 G, Pure, 795 G, 880 G, Heal, Coral Sword, Cabin, ...) match exactly.

Pass --items to list only the item chests (hide gold).
"""
import sys
from item_names import (get_weapon_names, get_armor_names, get_misc_names,
                        get_gold_names)

TREASURE = 0x3110
COUNT = 256


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    items_only = '--items' in sys.argv
    rom = args[0] if args else '../roms/Final Fantasy (USA).nes'
    try:
        with open(rom, 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        print(f"Error: ROM file '{rom}' not found")
        sys.exit(1)

    weapons, armor, misc, gold = (get_weapon_names(data), get_armor_names(data),
                                  get_misc_names(data), get_gold_names(data))

    def item_name(b):
        """Name for an item-range id (0x01-0x6b), or None if it's a gold chest."""
        if 1 <= b <= len(misc) and misc[b - 1]:
            return misc[b - 1]
        if 0x16 <= b <= 0x1b:
            return ['Tent', 'Cabin', 'House', 'Heal', 'Pure', 'Soft'][b - 0x16]
        if 0x1c <= b <= 0x43:
            return weapons[b - 0x1c]
        if 0x44 <= b <= 0x6b:
            return armor[b - 0x44]
        return None

    items = gold_chests = empty = 0
    for i in range(COUNT):
        b = data[TREASURE + i]
        if b == 0:
            empty += 1
            if not items_only:
                print(f"chest {i:3d}: (empty)")
            continue
        nm = item_name(b)
        if nm is not None:
            items += 1
            print(f"chest {i:3d}: {nm}")
        else:
            gold_chests += 1
            if not items_only:
                amount = gold[b - 0x6c] if 0x6c <= b < 0x6c + len(gold) else f'id 0x{b:02x}'
                print(f"chest {i:3d}: {amount}")

    print(f"\n{items} item chests, {gold_chests} gold chests, {empty} empty")


if __name__ == "__main__":
    main()
