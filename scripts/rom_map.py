"""Build a ROM memory-map / coverage analysis for Final Fantasy (USA).

Classifies every PRG byte as one of:
  * instruction - lives in a code bank (disassembled as 6502 code) and is not
                  inside a documented data table
  * data        - inside a structure we've documented and decode (named table,
                  graphics block, map data, ...)
  * unknown     - not yet characterised (raw data-bank bytes we haven't named,
                  e.g. music/sound data)

Authority: the FF1 disassembly's per-bank split (banks shipped as .asm are code,
.dat are data) plus the specific tables this project decodes (REGIONS below).
This is more complete than an FCEUX .cdl (which only marks bytes touched during a
play session); if roms/*.cdl is present it is parsed too, for a comparison column.

Outputs:
  output/rom_map.png   - 512x512 heatmap, 1 px/byte, bank gridlines
  output/rom_map.json  - banks, regions, and code/data/unknown totals (atlas)
"""
import glob
import json
import os
import sys
from PIL import Image, ImageDraw

HEADER = 0x10
BANK = 0x4000
NBANKS = 16
PRG = BANK * NBANKS

# Banks the FF1 disassembly ships as code (.asm); the rest are data (.dat).
CODE_BANKS = {0x1, 0x9, 0xB, 0xC, 0xD, 0xE, 0xF}
BANK_DESC = {
    0x0: "Tables: tilesets, tile props, TSA, palettes, domains, formations, treasure, teleports",
    0x1: "Overworld map data (RLE) + code", 0x2: "Overworld background CHR",
    0x3: "Standard-map tileset CHR", 0x4: "Standard-map data (RLE) + pointer table",
    0x5: "Standard-map data (cont.)", 0x6: "Standard-map data / graphics",
    0x7: "Enemy battle-sprite CHR", 0x8: "Enemy battle-sprite CHR (cont.)",
    0x9: "Battle CHR/palette loading code", 0xA: "Text: names, dialogue, battle messages",
    0xB: "Battle engine + monster names/formations/domains", 0xC: "Monster/weapon/armor/magic data + battle code",
    0xD: "Sound engine + item prices", 0xE: "Menus, shops, magic permissions",
    0xF: "Main engine: map loops, teleports, draw routines",
}

# Documented structures (file offset, size, name). Big graphics/map/text blocks
# are covered at bank granularity since the renderers decode them wholesale.
REGIONS = [
    (0x00010, 0x400, "Overworld tileset (prop/TSA/attr/palette)"),
    (0x00410, 0x400, "Standard-map metatile attributes"),
    (0x00810, 0x800, "Standard-map tile properties"),
    (0x01010, 0x1000, "Standard-map TSA (metatile definitions)"),
    (0x02010, 0xB80, "Standard-map palettes"),
    (0x02c10, 0xC0, "Teleport tables (entr/exit/norm)"),
    (0x02cd0, 0x40, "Map -> tileset table"),
    (0x03050, 0xC0, "Class starting stats"),
    (0x03110, 0x100, "Treasure chest contents"),
    (0x04010, 0x3000, "Overworld map data (RLE)"),
    (0x08010, 0x4000, "Overworld background CHR"),
    (0x0c010, 0x4000, "Standard-map tileset CHR"),
    (0x10010, 0x4000, "Standard-map data (RLE)"),
    (0x14010, 0x4000, "Standard-map data (cont.)"),
    (0x18010, 0x4000, "Standard-map data / graphics"),
    (0x1c010, 0x4000, "Enemy battle-sprite CHR"),
    (0x20010, 0x4000, "Enemy battle-sprite CHR (cont.)"),
    (0x28010, 0x1900, "Dialogue / battle message text"),
    (0x2b910, 0x100, "Quest/consumable item names"),
    (0x2b9cc, 0x447, "Weapon/armor names"),
    (0x2be13, 0x140, "Magic names"),
    (0x2c010, 0x400, "Battle domains (encounter zones)"),
    (0x2c410, 0x800, "Enemy formations"),
    (0x2cc10, 0x40, "Map encounter rates"),
    (0x2d010, 0x93, "EXP-to-level table"),
    (0x2d0a4, 0x24c, "Level-up growth data"),
    (0x2d5f0, 0x361, "Monster names"),
    (0x30010, 0x140, "Weapon data"),
    (0x30150, 0xA0, "Armor data"),
    (0x301f0, 0x200, "Magic data"),
    (0x30530, 0xA00, "Monster stats"),
    (0x30f30, 0x100, "Battle palettes"),
    (0x31030, 0x400, "Enemy AI scripts"),
    (0x37c10, 0x1e0, "Item prices"),
    (0x38310, 0x300, "Shop inventories"),
    (0x3ad28, 0x60, "Magic permissions"),
    (0x3ebc5, 0x47, "Shop types"),
]

# class codes: 0 instruction, 1 data, 2 unknown
COLOR = {0: (74, 120, 214), 1: (76, 174, 106), 2: (74, 80, 92)}


def classify(data):
    cls = bytearray(PRG)  # default 0 = instruction-or-unknown, set below
    for i in range(PRG):
        bank = i // BANK
        cls[i] = 0 if bank in CODE_BANKS else 2  # code bank -> code, data bank -> unknown
    for off, size, _ in REGIONS:
        a = off - HEADER
        for i in range(a, min(a + size, PRG)):
            cls[i] = 1  # documented data
    return cls


def render_png(cls, path):
    W = 512
    H = PRG // W
    img = Image.new('RGB', (W, H))
    px = img.load()
    for i in range(PRG):
        px[i % W, i // W] = COLOR[cls[i]]
    d = ImageDraw.Draw(img)
    rows_per_bank = BANK // W  # 32
    for b in range(1, NBANKS):
        y = b * rows_per_bank
        d.line([(0, y), (W, y)], fill=(20, 22, 28), width=1)
    img.resize((W * 2, H * 2), Image.NEAREST).save(path)


def cdl_compare():
    files = glob.glob('../roms/*.cdl')
    if not files:
        return None
    raw = open(files[0], 'rb').read()[:PRG]
    code = sum(1 for b in raw if b & 0x01)
    dat = sum(1 for b in raw if b & 0x02)
    unk = sum(1 for b in raw if (b & 0x03) == 0)
    return {'file': os.path.basename(files[0]), 'logged': len(raw),
            'code': code, 'data': dat, 'unknown': unk}


GHIDRA_SCRIPT = '''# FF1 ROM-map import for Ghidra (auto-generated by rom_map.py)
#
# Labels and plate-comments every data structure this project has decoded, on a
# Final Fantasy (USA) program loaded with the GhidraNes loader (MMC1 mapper).
# Run from the Script Manager (Tools > Script Manager) with the program open.
#
#@category FF1
#@menupath Tools.FF1.Apply ROM Map
from ghidra.program.model.symbol import SourceType

# (bank, offset_within_bank, size, name)
REGIONS = %s

def find_block(mem, bank):
    # GhidraNes/MMC1 names PRG banks "PRG<bb>"; swappable banks get _8/_C views.
    order = ["PRG%%02d_C" %% bank, "PRG%%02d" %% bank, "PRG%%02d_8" %% bank] if bank == 0x0F \\
            else ["PRG%%02d_8" %% bank, "PRG%%02d" %% bank, "PRG%%02d_C" %% bank]
    for nm in order:
        b = mem.getBlock(nm)
        if b is not None:
            return b
    return None

mem = currentProgram.getMemory()
applied = 0
for bank, off, size, name in REGIONS:
    blk = find_block(mem, bank)
    if blk is None:
        print("  no memory block for bank %%02X (%%s)" %% (bank, name)); continue
    addr = blk.getStart().add(off)
    sym = "ff1_" + "".join(c if (c.isalnum() or c == "_") else "_" for c in name)
    try:
        createLabel(addr, sym, True)
    except Exception as e:
        print("  label failed at %%s: %%s" %% (addr, e))
    setPlateComment(addr, "%%s (%%d bytes)" %% (name, size))
    applied += 1
print("FF1: applied %%d region labels/comments" %% applied)
'''


def emit_ghidra(out_dir):
    rg = [((off - HEADER) // BANK, (off - HEADER) % BANK, sz, n) for off, sz, n in REGIONS]
    # ImportSymbolsScript-compatible file (name <addr>); $8000 bank view, $C000 for fixed bank 0F
    lines = ["# FF1 documented data regions for Ghidra ImportSymbolsScript.",
             "# Address = CPU view of the byte when its bank is mapped in",
             "# ($8000 for swappable banks, $C000 for the fixed last bank 0F).",
             "# For bank-accurate placement use FF1_GhidraImport.py instead."]
    for bank, off, sz, n in rg:
        base = 0xC000 if bank == 0xF else 0x8000
        sym = "ff1_" + "".join(c if (c.isalnum() or c == "_") else "_" for c in n)
        lines.append(f"{sym} 0x{base + off:04x}")
    with open(os.path.join(out_dir, 'ff1_ghidra_symbols.txt'), 'w') as f:
        f.write('\n'.join(lines) + '\n')
    with open(os.path.join(out_dir, 'FF1_GhidraImport.py'), 'w') as f:
        f.write(GHIDRA_SCRIPT % repr(rg))


def main():
    rom = sys.argv[1] if len(sys.argv) > 1 else '../roms/Final Fantasy (USA).nes'
    out_dir = sys.argv[2] if len(sys.argv) > 2 else '../output'
    with open(rom, 'rb') as f:
        data = f.read()
    os.makedirs(out_dir, exist_ok=True)

    cls = classify(data)
    render_png(cls, os.path.join(out_dir, 'rom_map.png'))

    def cpu(bank):
        return "$C000" if bank == 0xF else "$8000"

    banks = []
    for b in range(NBANKS):
        seg = cls[b * BANK:(b + 1) * BANK]
        banks.append({'bank': b, 'cpu': cpu(b),
                      'role': 'code' if b in CODE_BANKS else 'data',
                      'desc': BANK_DESC[b],
                      'code': seg.count(0), 'data': seg.count(1), 'unknown': seg.count(2)})

    totals = {'code': cls.count(0), 'data': cls.count(1), 'unknown': cls.count(2), 'size': PRG}
    regions = [{'name': n, 'offset': off, 'size': sz, 'bank': (off - HEADER) // BANK}
               for off, sz, n in REGIONS]
    out = {'prg_size': PRG, 'bank_size': BANK, 'header': HEADER, 'banks': banks,
           'regions': regions, 'totals': totals, 'cdl': cdl_compare(),
           'colors': {'instruction': '#4a78d6', 'data': '#4cae6a', 'unknown': '#4a505c'}}
    with open(os.path.join(out_dir, 'rom_map.json'), 'w') as f:
        json.dump(out, f, separators=(',', ':'))

    emit_ghidra(out_dir)

    pct = lambda n: 100.0 * n / PRG
    print(f"PRG {PRG} bytes: instruction {pct(totals['code']):.1f}%  "
          f"data {pct(totals['data']):.1f}%  unknown {pct(totals['unknown']):.1f}%")
    print(f"wrote {out_dir}/rom_map.png and rom_map.json")


if __name__ == '__main__':
    main()
