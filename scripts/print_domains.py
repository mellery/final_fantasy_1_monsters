"""Print encounter zones (battle domains) from Final Fantasy (USA).

This is the "where do enemies appear" table. Each zone (domain) lists 8 battle
formations; GetBattleFormation picks one via a weighted RNG when an encounter
triggers. Which zone applies is COMPUTED from location (no lookup table) - per
the encounter code in bank_0F.asm ($C537 land, line 3304 standard maps):

  Overworld land : domain = (playerY>>5)*8 + (playerX>>5)   -> 0-63 (8x8 grid,
                   each cell = 32x32 overworld tiles)
  Overworld river: domain 0x40 (upper map half) / 0x41 (lower half)
  Overworld sea  : domain 0x42
  Standard maps  : domain = map_id + 0x40                    -> 64-127

So domains 0-63 are the overworld grid; 64-127 are the 64 standard maps (towns/
dungeons), and 64-66 double as the overworld river/sea zones.

  Battle domains: ROM offset 0x2c010, 128 domains x 8 bytes (one formation ref
                  per byte). Bit 7 of a ref selects the formation's "B" variant;
                  the low 7 bits are the formation index (into 0x2c410).
  Map encounter rates: 0x2cc10, 64 bytes (one rate per map; separate table).

Offsets confirmed by the Entroper/FF1Disassembly bin layout
(0B_8000_battledomains.bin, 0B_8400_battleformations.bin). Verified by
coherence: domains 18/20/24 are the imp-filled Coneria start, domain 115 is
the Sky Castle (WarMECH).
"""
import sys
from monster_names import get_names

DOMAINS = 0x2c010
NUM_DOMAINS = 128
FORMATIONS = 0x2c410


# Standard map id -> name (from the FF1Randomizer MapId enum, which is built on
# this same disassembly). Verified: map 51 = Sky Palace 5F, where WarMECH lives.
MAP_NAMES = {
    0: 'Coneria Town', 1: 'Pravoka', 2: 'Elfland', 3: 'Melmond',
    4: 'Crescent Lake', 5: 'Gaia', 6: 'Onrac', 7: 'Lefein',
    8: 'Coneria Castle 1F', 9: 'Elfland Castle', 10: 'Northwest Castle',
    11: 'Castle Ordeals 1F', 12: 'Temple of Fiends', 13: 'Earth Cave B1',
    14: 'Gurgu Volcano B1', 15: 'Ice Cave B1', 16: 'Cardia', 17: 'Bahamut Cave B1',
    18: 'Waterfall', 19: 'Dwarf Cave', 20: "Matoya's Cave", 21: "Sarda's Cave",
    22: 'Marsh Cave B1', 23: 'Mirage Tower 1F', 24: 'Coneria Castle 2F',
    25: 'Castle Ordeals 2F', 26: 'Castle Ordeals 3F', 27: 'Marsh Cave B2',
    28: 'Marsh Cave B3', 29: 'Earth Cave B2', 30: 'Earth Cave B3',
    31: 'Earth Cave B4', 32: 'Earth Cave B5', 33: 'Gurgu Volcano B2',
    34: 'Gurgu Volcano B3', 35: 'Gurgu Volcano B4', 36: 'Gurgu Volcano B5',
    37: 'Ice Cave B2', 38: 'Ice Cave B3', 39: 'Bahamut Cave B2',
    40: 'Mirage Tower 2F', 41: 'Mirage Tower 3F', 42: 'Sea Shrine B5',
    43: 'Sea Shrine B4', 44: 'Sea Shrine B3', 45: 'Sea Shrine B2',
    46: 'Sea Shrine B1', 47: 'Sky Palace 1F', 48: 'Sky Palace 2F',
    49: 'Sky Palace 3F', 50: 'Sky Palace 4F', 51: 'Sky Palace 5F',
    52: 'ToF Revisited 1F', 53: 'ToF Revisited 2F', 54: 'ToF Revisited 3F',
    55: 'ToFR Earth', 56: 'ToFR Fire', 57: 'ToFR Water', 58: 'ToFR Air',
    59: 'ToFR Chaos', 60: "Titan's Tunnel",
}


def zone_location(d):
    """What location uses this domain (per bank_0F.asm encounter code)."""
    if d < 0x40:
        return f"OW grid col{d & 7},row{d >> 3}"
    mname = MAP_NAMES.get(d - 0x40, f"map {d - 0x40}")
    ow = {0x40: 'OW river-N', 0x41: 'OW river-S', 0x42: 'OW sea'}.get(d)
    return f"{ow} / {mname}" if ow else mname


def main():
    rom = sys.argv[1] if len(sys.argv) > 1 else '../roms/Final Fantasy (USA).nes'
    try:
        with open(rom, 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        print(f"Error: ROM file '{rom}' not found")
        sys.exit(1)

    names = get_names(data)

    def nm(i):
        return names[i] if i < len(names) else f'#{i}'

    def formation_summary(ref):
        """Lead monsters of the formation a domain byte points at (bit7 = B)."""
        idx = ref & 0x7f
        e = data[FORMATIONS + idx * 16: FORMATIONS + idx * 16 + 16]
        is_b = ref & 0x80
        mons = []
        slots = range(2) if is_b else range(4)
        qoff = 0xe if is_b else 6
        for s in slots:
            eid = e[2 + s]
            mx = e[qoff + s] & 0x0f
            if eid < 0x80 and mx > 0:
                mons.append(nm(eid))
        tag = f"f{idx}{'B' if is_b else ''}"
        return f"{tag}[{','.join(mons) if mons else '-'}]"

    for d in range(NUM_DOMAINS):
        refs = data[DOMAINS + d * 8: DOMAINS + d * 8 + 8]
        formations = ' '.join(formation_summary(r) for r in refs)
        print(f"zone {d:3d} [{zone_location(d):24}]: {formations}")


if __name__ == "__main__":
    main()
