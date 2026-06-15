"""Print character class data from Final Fantasy (USA): starting stats, the EXP
table, and per-class level-up growth.

Offsets from the FF1 disassembly:
  Class starting stats : lut_ClassStartingStats $B040 bank 0 = file 0x3050,
                         16 bytes/class: [classid, HP, Str, Agi, Int, Vit, Luck, ...]
  EXP to advance       : lut_ExpToAdvance $9000 bank 0B = file 0x2d010,
                         3 bytes LE per level (level N -> N+1), 49 entries
  Level-up data        : data_LevelUpData_Raw $9094 = file 0x2d0a4, 49 levels x
                         2 bytes per class, 6 classes contiguous (98 bytes each):
                           byte 0: bit5 strong HP, bit4 Str, bit3 Agi, bit2 Int,
                                   bit1 Vit, bit0 Luck (guaranteed increases)
                           byte 1: MP up - each bit is a spell level gained

Verified: Fighter starts HP 35 / Str 20 / Agi 5 / Int 1 / Vit 10 / Luck 5;
EXP to level 2 = 40.
"""
import sys

START, EXP, LVLUP = 0x3050, 0x2d010, 0x2d0a4
CLASS_NAMES = ['Fighter', 'Thief', 'BlackBelt', 'RedMage', 'WhiteMage', 'BlackMage']
STAT_BITS = [(0x10, 'Str'), (0x08, 'Agi'), (0x04, 'Int'), (0x02, 'Vit'), (0x01, 'Luck')]


def starting_stats(data, cls):
    b = data[START + cls * 16: START + cls * 16 + 16]
    return dict(HP=b[1], Str=b[2], Agi=b[3], Int=b[4], Vit=b[5], Luck=b[6])


def exp_to_advance(data, lv):  # lv = 1..49 (level lv -> lv+1)
    o = EXP + (lv - 1) * 3
    return data[o] | (data[o + 1] << 8) | (data[o + 2] << 16)


def levelup_summary(data, cls):
    """Count, over the 49 level-ups, how often each stat is guaranteed + MP-up levels."""
    base = LVLUP + cls * 98
    counts = {n: 0 for _, n in STAT_BITS}
    strong = mp = 0
    for lv in range(49):
        b0, b1 = data[base + lv * 2], data[base + lv * 2 + 1]
        for bit, n in STAT_BITS:
            if b0 & bit:
                counts[n] += 1
        if b0 & 0x20:
            strong += 1
        if b1:
            mp += 1
    return counts, strong, mp


def main():
    rom = sys.argv[1] if len(sys.argv) > 1 else '../roms/Final Fantasy (USA).nes'
    with open(rom, 'rb') as f:
        data = f.read()

    print("=== STARTING STATS ===")
    print(f"{'class':10} {'HP':>3} {'Str':>3} {'Agi':>3} {'Int':>3} {'Vit':>3} {'Luck':>4}")
    for c, name in enumerate(CLASS_NAMES):
        s = starting_stats(data, c)
        print(f"{name:10} {s['HP']:3} {s['Str']:3} {s['Agi']:3} {s['Int']:3} {s['Vit']:3} {s['Luck']:4}")

    print("\n=== LEVEL-UP GROWTH (guaranteed stat increases over 49 level-ups) ===")
    print(f"{'class':10} {'Str':>3} {'Agi':>3} {'Int':>3} {'Vit':>3} {'Luck':>4}  {'strongHP':>8} {'MPlvls':>6}")
    for c, name in enumerate(CLASS_NAMES):
        counts, strong, mp = levelup_summary(data, c)
        print(f"{name:10} {counts['Str']:3} {counts['Agi']:3} {counts['Int']:3} "
              f"{counts['Vit']:3} {counts['Luck']:4}  {strong:8} {mp:6}")

    print("\n=== EXP TO ADVANCE (level N -> N+1) ===")
    for lv in range(1, 50):
        end = '\n' if lv % 7 == 0 else '  '
        print(f"L{lv:2}->{lv+1:2}:{exp_to_advance(data, lv):7}", end=end)
    print()


if __name__ == "__main__":
    main()
