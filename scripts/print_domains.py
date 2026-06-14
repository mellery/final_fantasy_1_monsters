"""Print encounter zones (battle domains) from Final Fantasy (USA).

This is the "where do enemies appear" table. The overworld grid and each
dungeon map reference a domain index (0-127); the domain lists the 8 battle
formations that can be randomly rolled in that zone.

  Battle domains: ROM offset 0x2c000, 128 domains x 8 bytes (one formation ref
                  per byte). Bit 7 of a ref selects the formation's "B" variant;
                  the low 7 bits are the formation index (into 0x2c400).
  Map encounter rates: 0x2cc00, 64 bytes (one rate per map; separate table).

Offsets confirmed by the Entroper/FF1Disassembly bin layout
(0B_8000_battledomains.bin, 0B_8400_battleformations.bin). Verified by
coherence: e.g. domain 1 is the endgame zone (WarMECH, NITEMARE, EVILMAN).
"""
import sys
from monster_names import get_names

DOMAINS = 0x2c000
NUM_DOMAINS = 128
FORMATIONS = 0x2c400


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
        print(f"zone {d:3d}: {formations}")


if __name__ == "__main__":
    main()
