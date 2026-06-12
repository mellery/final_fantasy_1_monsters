"""Print the 40 weapon records from Final Fantasy (USA).

Weapon data table: ROM offset 0x30010, 40 entries x 8 bytes:
  0: hit% bonus
  1: damage
  2: critical hit %
  3: spell index cast when the weapon is "used" as an item in battle (0 = none)
  4: element (bitfield, see ELEMENTS)
  5: monster-family bonus - extra damage vs this family (bitfield, see FAMILIES)
  6: battle sprite/graphic index
  7: sprite palette index
"""
import os
import struct
import sys
from item_names import get_weapon_names, decode_bits, ELEMENTS, FAMILIES

WEAPON_DATA = 0x30010
COUNT = 40
SIZE = 8


def main():
    rom = sys.argv[1] if len(sys.argv) > 1 else '../roms/Final Fantasy (USA).nes'
    try:
        with open(rom, 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        print(f"Error: ROM file '{rom}' not found")
        sys.exit(1)

    names = get_weapon_names(data)
    print(f"{'#':>2} {'NAME':8} {'DMG':>3} {'HIT':>3} {'CRIT':>4}  {'ELEMENT':12} {'VS FAMILY':10} {'SPELL':5}")
    print('-' * 60)
    for i in range(COUNT):
        b = data[WEAPON_DATA + i * SIZE: WEAPON_DATA + i * SIZE + SIZE]
        hit, dmg, crit, spell, elem, family, sprite, pal = b
        name = names[i] if i < len(names) else f'weapon{i}'
        print(f"{i:2d} {name:8} {dmg:3d} {hit:3d} {crit:4d}  "
              f"{decode_bits(elem, ELEMENTS):12} {decode_bits(family, FAMILIES):10} "
              f"{spell if spell else '-':>5}")


if __name__ == "__main__":
    main()
