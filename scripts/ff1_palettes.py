"""Battle palettes and per-monster palette assignment for Final Fantasy (USA).

Battle palette table: ROM 0x30f30 (0C_8F20_battlepalettes.bin), 64 palettes x
4 bytes, each byte an NES color index (low 6 bits). Color 0 is the backdrop.

A monster's colors aren't stored on the monster; they come from the formation
it appears in. Per the battle-setup code (bank_0B.asm ~line 2148): for enemy
slot s, bit (7-s) of formation byte D selects palette A (byte A) or B (byte B),
each an index into the battle palette table.

get_monster_palettes() resolves each monster to the palette of the first
formation that uses it. Verified: IMP/WOLF = tan/orange, FrWOLF = icy blue/white,
CARIBE = aquatic cyan/green.
"""
from nes_color_converter import NES_PALETTE

BATTLE_PALETTES = 0x30f30
FORMATIONS = 0x2c410
NUM_FORMATIONS = 128


def get_battle_palettes(data):
    """Return 64 palettes, each a list of 4 (r,g,b) tuples."""
    pals = []
    for p in range(64):
        idxs = data[BATTLE_PALETTES + p * 4: BATTLE_PALETTES + p * 4 + 4]
        pals.append([NES_PALETTE[c & 0x3f] for c in idxs])
    return pals


def get_monster_palettes(data):
    """Map monster id -> (palette_id, [4 (r,g,b)]) via the first formation it's in."""
    pals = get_battle_palettes(data)
    raw_pals = [list(data[BATTLE_PALETTES + p * 4: BATTLE_PALETTES + p * 4 + 4])
                for p in range(64)]
    result = {}
    for f in range(NUM_FORMATIONS):
        e = data[FORMATIONS + f * 16: FORMATIONS + f * 16 + 16]
        for s in range(4):
            eid = e[2 + s]
            qmax = e[6 + s] & 0x0f
            if eid < 0x80 and qmax > 0 and eid not in result:
                sel = (e[0xd] >> (7 - s)) & 1
                pid = e[0xa] if sel == 0 else e[0xb]
                result[eid] = (pid, pals[pid], raw_pals[pid])
    return result
