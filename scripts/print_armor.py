"""Print the 40 armor records from Final Fantasy (USA).

Armor data table: ROM offset 0x30150, 40 entries x 4 bytes:
  0: weight (evade % penalty)
  1: defense
  2: element resistance (bitfield, see ELEMENTS)
  3: extra resistance / status flag (mostly 0; shown raw)
"""
import os
import sys
from item_names import get_armor_names, decode_bits, ELEMENTS

ARMOR_DATA = 0x30150
COUNT = 40
SIZE = 4


def main():
    rom = sys.argv[1] if len(sys.argv) > 1 else '../roms/Final Fantasy (USA).nes'
    try:
        with open(rom, 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        print(f"Error: ROM file '{rom}' not found")
        sys.exit(1)

    names = get_armor_names(data)
    print(f"{'#':>2} {'NAME':8} {'DEF':>3} {'WT':>3}  {'RESIST':16} {'B3':>3}")
    print('-' * 44)
    for i in range(COUNT):
        weight, defense, resist, b3 = data[ARMOR_DATA + i * SIZE: ARMOR_DATA + i * SIZE + SIZE]
        name = names[i] if i < len(names) else f'armor{i}'
        print(f"{i:2d} {name:8} {defense:3d} {weight:3d}  "
              f"{decode_bits(resist, ELEMENTS):16} {b3:#04x}")


if __name__ == "__main__":
    main()
