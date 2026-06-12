"""Print buy prices for every item in Final Fantasy (USA).

Price table: ROM offset 0x37c10, indexed by item id, 2 bytes little-endian.
Quest items (0x01-0x15) are 0 (not for sale). Magic (0xb0-0xef) is priced by
spell level: 100/400/1500/4000/8000/20000/45000/60000 gold for levels 1-8.

Verified against canonical FF1: consumables Tent=75/Cabin=250/Heal=60/Pure=75/
Soft=800, the 'Power' item's 12345 placeholder, Opal armor 65000.
"""
import sys
from item_names import (build_item_id_map, get_weapon_names, get_armor_names,
                        get_magic_names, get_price)


def main():
    rom = sys.argv[1] if len(sys.argv) > 1 else '../roms/Final Fantasy (USA).nes'
    try:
        with open(rom, 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        print(f"Error: ROM file '{rom}' not found")
        sys.exit(1)

    weapons, armor, magic = get_weapon_names(data), get_armor_names(data), get_magic_names(data)

    def section(title, names, base):
        print(f"\n=== {title} ===")
        for i, nm in enumerate(names):
            print(f"  {nm:9s} {get_price(data, base + i):6d} G")

    # Consumables (ids 0x16-0x1b)
    print("=== CONSUMABLES ===")
    for idv, nm in [(0x16, 'Tent'), (0x17, 'Cabin'), (0x18, 'House'),
                    (0x19, 'Heal'), (0x1a, 'Pure'), (0x1b, 'Soft')]:
        print(f"  {nm:9s} {get_price(data, idv):6d} G")

    section('WEAPONS', weapons, 0x1c)
    section('ARMOR', armor, 0x44)
    section('MAGIC', magic, 0xb0)


if __name__ == "__main__":
    main()
