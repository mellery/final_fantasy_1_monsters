"""Print shop inventories from Final Fantasy (USA).

A pointer table at ROM offset 0x38310 holds little-endian CPU pointers
($8000-mapped bank, so file offset = pointer + 0x30000). Each pointer leads to
a shop's stock: a list of item ids terminated by 0x00. Unused shop slots point
back into the pointer table region (pointer < 0x839f) and are skipped.

Item ids share one namespace (see item_names.build_item_id_map): quest items,
consumables, weapons, armor, and magic. The shop type is inferred from its
contents.
"""
import os
import struct
import sys
from item_names import (build_item_id_map, get_weapon_names, get_armor_names,
                        get_magic_names, get_misc_names)

PTR_TABLE = 0x38310
NUM_SHOPS = 71
BANK_TO_FILE = 0x30000
DATA_START = 0x839f  # pointers below this address are unused slots


def is_sellable(i):
    """Ids a shop can actually stock: consumables, weapons, armor, magic.

    Clinic/caravan slots store a gold price instead of an item list, and unused
    slots point at leftover bytes; both decode into quest items (0x01-0x11) or
    the 0x6c-0xaf gap, so requiring sellable ids filters them out.
    """
    return (0x16 <= i <= 0x6b) or (0xb0 <= i <= 0xef)


def classify(ids):
    def kind(i):
        if 0x1c <= i <= 0x43:
            return 'weapon'
        if 0x44 <= i <= 0x6b:
            return 'armor'
        if 0xb0 <= i <= 0xef:
            return 'magic'
        return 'item'
    kinds = {kind(i) for i in ids}
    if len(kinds) == 1:
        return {'weapon': 'WEAPON', 'armor': 'ARMOR',
                'magic': 'MAGIC', 'item': 'ITEM'}[kinds.pop()]
    return 'MIXED'


def main():
    rom = sys.argv[1] if len(sys.argv) > 1 else '../roms/Final Fantasy (USA).nes'
    try:
        with open(rom, 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        print(f"Error: ROM file '{rom}' not found")
        sys.exit(1)

    id_map = build_item_id_map(data)

    def name(i):
        return id_map.get(i, f'item:{i:02x}')

    shown = 0
    for s in range(NUM_SHOPS):
        ptr = struct.unpack_from('<H', data, PTR_TABLE + s * 2)[0]
        if ptr < DATA_START:
            continue  # unused/empty shop slot
        off = ptr + BANK_TO_FILE
        ids = []
        j = off
        while j < len(data) and data[j] != 0x00:
            ids.append(data[j])
            j += 1
        if not ids or not all(is_sellable(i) for i in ids):
            continue  # clinic/caravan (price) or unused slot
        items = ', '.join(name(i) for i in ids)
        print(f"shop {s:2d} [{classify(ids):6}]: {items}")
        shown += 1

    print(f"\n{shown} stocked inventory shops "
          f"(clinic/caravan price slots and town labels not decoded)")


if __name__ == "__main__":
    main()
