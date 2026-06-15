"""Decode the magic-learning permission tables: which character class can learn
each of the 64 spells.

Source: lut_MagicPermisPtr and the per-class tables in bank 0E
(MagicShop_AssertLearn). ROM file offset 0x3ad28 holds 12 classes x 8 bytes.
Each byte is one spell level (1-8); within a byte the 8 spells of that level use
bit mask 0x80 >> position (lut_BIT). Positions 0-3 are White magic, 4-7 Black.
A CLEAR bit means the class CAN learn that spell (the game does AND then
BEQ HasPermission); a set bit forbids it.

Verified vs ROM: WhiteWizard = all white (0x0f x8), BlackWizard = all black
(0xf0 x8), Fighter/Thief/BlackBelt/Master = none (0xff x8), RedMage learns both
schools but not the level-8 tier.
"""
import sys
from item_names import get_magic_names

MAGIC_PERMS = 0x3ad28
CLASS_NAMES = ['Fighter', 'Thief', 'BlackBelt', 'RedMage', 'WhiteMage', 'BlackMage',
               'Knight', 'Ninja', 'Master', 'RedWizard', 'WhiteWizard', 'BlackWizard']


def get_magic_permissions(data):
    """Return 64 dicts: {id, name, level (1-8), school, classes:[names]}."""
    names = get_magic_names(data)
    out = []
    for sid in range(64):
        lvl, pos = sid // 8, sid % 8
        mask = 0x80 >> pos
        learners = [CLASS_NAMES[c] for c in range(12)
                    if (data[MAGIC_PERMS + c * 8 + lvl] & mask) == 0]
        out.append({'id': sid, 'name': names[sid], 'level': lvl + 1,
                    'school': 'White' if pos < 4 else 'Black', 'classes': learners})
    return out


def main():
    rom = sys.argv[1] if len(sys.argv) > 1 else '../roms/Final Fantasy (USA).nes'
    with open(rom, 'rb') as f:
        data = f.read()
    perms = get_magic_permissions(data)
    print(f"{'Lv':>2} {'School':5} {'Spell':5}  Learnable by")
    print('-' * 60)
    for p in perms:
        print(f"{p['level']:2} {p['school']:5} {p['name']:5}  "
              f"{', '.join(p['classes']) or '(none)'}")


if __name__ == '__main__':
    main()
