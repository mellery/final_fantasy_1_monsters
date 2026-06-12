"""Print the 64 magic spell records from Final Fantasy (USA).

Magic data table: ROM offset 0x301f0, 64 entries x 8 bytes:
  0: accuracy (hit %)
  1: effectivity (power - damage, heal amount, etc.)
  2: element (bitfield, see ELEMENTS)
  3: target (bitfield, see TARGETS)
  4: effect routine index (how the spell is applied)
  5: animation graphic index
  6: animation palette index
  7: unused (0)

Spell names: 64 x 5-byte entries at 0x2be13.
"""
import os
import sys
from item_names import get_magic_names, decode_bits, ELEMENTS, TARGETS

MAGIC_DATA = 0x301f0
COUNT = 64
SIZE = 8


def main():
    rom = sys.argv[1] if len(sys.argv) > 1 else '../roms/Final Fantasy (USA).nes'
    try:
        with open(rom, 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        print(f"Error: ROM file '{rom}' not found")
        sys.exit(1)

    names = get_magic_names(data)
    print(f"{'#':>2} {'NAME':5} {'ACC':>3} {'EFF':>3}  {'ELEMENT':8} {'TARGET':11} {'RTN':>4}")
    print('-' * 46)
    for i in range(COUNT):
        b = data[MAGIC_DATA + i * SIZE: MAGIC_DATA + i * SIZE + SIZE]
        acc, eff, elem, target, routine = b[0], b[1], b[2], b[3], b[4]
        name = names[i] if i < len(names) else f'sp{i}'
        print(f"{i:2d} {name:5} {acc:3d} {eff:3d}  "
              f"{decode_bits(elem, ELEMENTS):8} {decode_bits(target, TARGETS):11} {routine:#04x}")


if __name__ == "__main__":
    main()
