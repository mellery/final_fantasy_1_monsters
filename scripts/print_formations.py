"""Print enemy formations (encounter battle groups) from Final Fantasy (USA).

Formation table: ROM offset 0x2c410, 128 entries x 16 bytes. Format from the
FF1 disassembly (Entroper/FF1Disassembly, "some formats.txt"):

  byte 0   : high nibble = battle type (0=9 small, 1=4 large, 2=mixed,
             3=fiend, 4=chaos), low nibble = layout pattern
  byte 1   : enemy picture assignment (2 bits per slot)
  bytes 2-5: enemy ids for the 4 slots (monster index, 0xff = unused)
  bytes 6-9: per-slot quantity, high nibble = min, low nibble = max
  bytes A-B: palette ids
  byte C   : surprise rate
  byte D   : bit 0 = "no run" flag; high nibble = palette assignment
  bytes E-F: "formation B" quantities for slots 0-1 (an alternate group)

Verified: formation 1 is 3-5 IMP (the first overworld battle).
"""
import sys
from monster_names import get_names

FORMATIONS = 0x2c410
COUNT = 128
SIZE = 16
TYPES = {0: '9-small', 1: '4-large', 2: 'mixed', 3: 'fiend', 4: 'chaos'}


def main():
    rom = sys.argv[1] if len(sys.argv) > 1 else '../roms/Final Fantasy (USA).nes'
    try:
        with open(rom, 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        print(f"Error: ROM file '{rom}' not found")
        sys.exit(1)

    names = get_names(data)

    def name(i):
        return names[i] if i < len(names) else f'#{i}'

    for k in range(COUNT):
        e = data[FORMATIONS + k * SIZE: FORMATIONS + k * SIZE + SIZE]
        btype = TYPES.get(e[0] >> 4, str(e[0] >> 4))
        norun = ' noRUN' if e[0xd] & 1 else ''

        # Formation A: slots with a real id and max count > 0
        groups = []
        for s in range(4):
            eid = e[2 + s]
            mn, mx = e[6 + s] >> 4, e[6 + s] & 0x0f
            if eid < 0x80 and mx > 0:
                groups.append(f"{mn}-{mx} {name(eid)}")
        if not groups:
            continue  # unused formation slot

        # Formation B: alternate quantities for slots 0-1 (bytes E-F)
        bgroups = []
        for s in range(2):
            eid = e[2 + s]
            mn, mx = e[0xe + s] >> 4, e[0xe + s] & 0x0f
            if eid < 0x80 and mx > 0:
                bgroups.append(f"{mn}-{mx} {name(eid)}")

        line = f"{k:3d} [{btype:7}]{norun}  " + "; ".join(groups)
        if bgroups:
            line += "   | B: " + "; ".join(bgroups)
        print(line)


if __name__ == "__main__":
    main()
