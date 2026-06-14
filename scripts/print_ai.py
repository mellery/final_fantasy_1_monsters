"""Print enemy AI scripts from Final Fantasy (USA).

Each monster's stat byte 7 is its AI index (0xff = no AI, just attacks). The AI
table lut_EnemyAi is at ROM 0x31030, 16 bytes per entry:
  byte 0   : magic rate   (0-0x80 chance per turn to cast instead of attack)
  byte 1   : skill rate    (chance to use a special attack)
  bytes 2-9: 8 spell slots  (spell id 0-63, cycled in order; 0xff = empty)
  byte A   : unused
  bytes B-E: 4 skill slots  (special-attack id; 0xff = empty)
  byte F   : unused

Spell ids index the magic table (player spells, names at 0x2be13). Skill ids
index the extended effect table at magicentry (skill + 0x42): the 8-byte magic
records run 0-103 (0x301f0), where 0-63 are spells and 0x42+ are enemy skills.

Format from Entroper/FF1Disassembly (some formats.txt, Enemy_DoAi in bank_0C).
Verified: MAGE casts FIR3/LIT3, KARY casts FIR2/FIR3, Frost D's skill = Ice.
"""
import sys
from monster_names import get_names
from item_names import get_magic_names, decode_bits, ELEMENTS

MONSTERS = 0x30530
AI_TABLE = 0x31030
MAGIC_DATA = 0x301f0


def main():
    rom = sys.argv[1] if len(sys.argv) > 1 else '../roms/Final Fantasy (USA).nes'
    try:
        with open(rom, 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        print(f"Error: ROM file '{rom}' not found")
        sys.exit(1)

    names = get_names(data)
    magic = get_magic_names(data)

    def spell_name(s):
        return magic[s] if s < len(magic) else f'spell{s:02x}'

    def skill_desc(s):
        """An enemy skill's element, from the extended magic-effect table."""
        e = data[MAGIC_DATA + (s + 0x42) * 8: MAGIC_DATA + (s + 0x42) * 8 + 8]
        return f"sk{s:02x}({decode_bits(e[2], ELEMENTS)})"

    for mid in range(128):
        ai = data[MONSTERS + mid * 20 + 7]
        if ai == 0xff:
            continue
        e = data[AI_TABLE + ai * 16: AI_TABLE + ai * 16 + 16]
        mag_rate, skl_rate = e[0], e[1]
        spells = [spell_name(e[2 + i]) for i in range(8) if e[2 + i] != 0xff]
        skills = [skill_desc(e[0xb + i]) for i in range(4) if e[0xb + i] != 0xff]

        parts = []
        if spells:
            parts.append(f"magic {mag_rate*100//128}%: {', '.join(spells)}")
        if skills:
            parts.append(f"skill {skl_rate*100//128}%: {', '.join(skills)}")
        print(f"{names[mid]:9s} (ai {ai:2d})  " + "   ".join(parts))


if __name__ == "__main__":
    main()
