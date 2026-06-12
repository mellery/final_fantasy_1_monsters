"""Shared name + bitfield helpers for Final Fantasy (USA) data tables.

Weapon and armor names live in a single packed stream of 0x00-delimited
strings at ROM offset 0x2b9cc: entries 0-39 are weapons, 40-79 are armor.
Each entry is the display text plus trailing "icon" tiles (high bytes not in
the character table), which we drop. Magic spell names are a clean fixed-width
table of 5-byte entries at 0x2be13.
"""
import os
from load_tbl import generate_character_map

TBL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools', 'final_fantasy.tbl')
characters = generate_character_map(TBL_PATH)

EQUIP_NAME_STREAM = 0x2b9cc   # weapon names (0-39) then armor names (40-79)
MAGIC_NAMES = 0x2be13         # 64 spell names, 5 bytes each

# Element bitfield (shared by weapons, magic, and monster weak/resist fields)
ELEMENTS = [
    (0x01, 'Status'), (0x02, 'Poison'), (0x04, 'Time'), (0x08, 'Death'),
    (0x10, 'Fire'),   (0x20, 'Ice'),    (0x40, 'Lit'),  (0x80, 'Earth'),
]

# Monster-family bitfield (weapon "effective against" bonus shares this)
FAMILIES = [
    (0x02, 'Dragon'), (0x04, 'Giant'), (0x08, 'Undead'), (0x10, 'Were'),
    (0x20, 'Aquatic'), (0x40, 'Mage'), (0x80, 'Regen'),
]

# Magic target bitfield
TARGETS = [
    (0x01, 'AllEnemies'), (0x02, 'OneEnemy'), (0x04, 'Self'),
    (0x08, 'AllAllies'), (0x10, 'OneAlly'),
]


def decode_bits(value, table):
    """Return a '|'-joined list of set bit names, or '-' if none."""
    if value == 0xff:
        return 'All'
    names = [name for bit, name in table if value & bit]
    leftover = value & ~sum(bit for bit, _ in table)
    if leftover:
        names.append(f'0x{leftover:02x}')
    return '|'.join(names) if names else '-'


def _decode_entry(data, start, length):
    """Decode tbl text for one entry, dropping non-text (icon) bytes."""
    out = ''
    for x in data[start:start + length]:
        if x == 0x00:
            break
        key = bytes([x])
        if key in characters:
            out += characters[key]
    return out.strip()


def get_equip_names(data):
    """Return the packed weapon+armor name list (0x00-delimited stream)."""
    names = []
    cur = ''
    i = EQUIP_NAME_STREAM
    while len(names) < 80 and i < len(data):
        x = data[i]
        if x == 0x00:
            if cur:
                names.append(cur.strip())
                cur = ''
        else:
            key = bytes([x])
            if key in characters:
                cur += characters[key]
        i += 1
    return names


def get_weapon_names(data):
    return get_equip_names(data)[0:40]


def get_armor_names(data):
    return get_equip_names(data)[40:80]


def get_magic_names(data):
    return [_decode_entry(data, MAGIC_NAMES + i * 5, 5) for i in range(64)]


MISC_NAMES = 0x2b910  # quest items + consumables, 0x00-delimited, IDs start at 0x01


def get_misc_names(data):
    """Quest/consumable item names as a 0x00-delimited stream (ID = index+1).

    IDs 0x12-0x15 are unused (a blank record), so this list includes empty
    strings at those positions to keep IDs aligned: 0x16=TENT .. 0x1b=SOFT.
    """
    names = []
    cur = ''
    i = MISC_NAMES
    while i < EQUIP_NAME_STREAM:
        x = data[i]
        if x == 0x00:
            names.append(cur.strip())
            cur = ''
        else:
            key = bytes([x])
            if key in characters:
                cur += characters[key]
        i += 1
    names.append(cur.strip())  # flush the final entry (SOFT has no trailing 0x00)
    return names[1:]  # first split is the empty lead-in before LUTE


def build_item_id_map(data):
    """Unified shop/treasure item-id -> name, verified against shop contents.

    0x01-0x11 quest items, 0x16-0x1b consumables, 0x1c-0x43 weapons,
    0x44-0x6b armor, 0xb0-0xef magic. Unmapped ids render as 'item:NN'.
    """
    weapons, armor, magic, misc = (
        get_weapon_names(data), get_armor_names(data),
        get_magic_names(data), get_misc_names(data))
    id_map = {}
    for i, nm in enumerate(misc):
        if nm:
            id_map[i + 1] = nm
    for i, nm in enumerate(weapons):
        id_map[0x1c + i] = nm
    for i, nm in enumerate(armor):
        id_map[0x44 + i] = nm
    for i, nm in enumerate(magic):
        id_map[0xb0 + i] = nm
    return id_map
