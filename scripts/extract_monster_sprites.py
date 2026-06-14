"""Extract every monster sprite in color from Final Fantasy (USA).

Each monster maps to a sprite slot via its formations:
  CHR page   = formation byte 0 low nibble (which 0x800 CHR page is loaded)
  gfx (0-3)  = (formation byte 1 >> (2*slot)) & 3, where bit0 = size
               (0 = small 4x4, 1 = medium 6x6) and bit1 = image (0 or 1)

CHR page -> ROM base:  page 0-7 at 0x1c000 + page*0x800,
                       page 8-15 at 0x20000 + (page-8)*0x800.
Within a page the four enemy sprites sit at fixed offsets (verified visually):
  gfx 0 (small img0) +0x130   gfx 2 (small img1) +0x230
  gfx 1 (med   img0) +0x330   gfx 3 (med   img1) +0x570

The sprite tiles are colored with the monster's battle palette (ff1_palettes):
tile value 0 -> transparent, 1/2/3 -> the palette's three colors.

Pages 13-15 are the fiends/Chaos, which use a different (TSA) tile arrangement;
those are extracted by find_ff1_monster_tiles.py and colored with
colorize_monster.py instead. This script handles every other monster.
"""
import os
import sys
import numpy as np
from PIL import Image
from monster_names import get_names
from ff1_palettes import get_monster_palettes

FORMATIONS = 0x2c410
# gfx index -> (offset within page, width, height in tiles)
GFX_SLOT = {0: (0x130, 4, 4), 2: (0x230, 4, 4), 1: (0x330, 6, 6), 3: (0x570, 6, 6)}


def page_base(page):
    return 0x1c000 + page * 0x800 if page < 8 else 0x20000 + (page - 8) * 0x800


def decode_tile(data, off):
    t = np.zeros((8, 8), int)
    for i in range(8):
        lo, hi = data[off + i], data[off + i + 8]
        for j in range(8):
            t[i, j] = ((lo >> (7 - j)) & 1) | (((hi >> (7 - j)) & 1) << 1)
    return t


def render_sprite(data, base, w, h, palette):
    """Assemble a w*h tile grid and color it with the 4-entry palette (RGBA)."""
    img = Image.new('RGBA', (w * 8, h * 8))
    px = img.load()
    for n in range(w * h):
        t = decode_tile(data, base + n * 16)
        ox, oy = (n % w) * 8, (n // w) * 8
        for y in range(8):
            for x in range(8):
                v = t[y, x]
                px[ox + x, oy + y] = palette[v] + (0,) if v == 0 else palette[v] + (255,)
    return img


def main():
    rom = sys.argv[1] if len(sys.argv) > 1 else '../roms/Final Fantasy (USA).nes'
    out_dir = sys.argv[2] if len(sys.argv) > 2 else '../output/monsters'
    try:
        with open(rom, 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        print(f"Error: ROM file '{rom}' not found")
        sys.exit(1)

    os.makedirs(out_dir, exist_ok=True)
    names = get_names(data)
    palettes = get_monster_palettes(data)

    # monster -> (page, gfx) from the first formation that uses it
    slot = {}
    for f in range(128):
        e = data[FORMATIONS + f * 16: FORMATIONS + f * 16 + 16]
        for s in range(4):
            eid = e[2 + s]
            if eid < 0x80 and (e[6 + s] & 0x0f) > 0 and eid not in slot:
                slot[eid] = (e[0] & 0x0f, (e[1] >> (2 * s)) & 3)

    done = boss = skipped = 0
    for mid in range(128):
        if mid not in slot or mid not in palettes:
            skipped += 1
            continue
        page, gfx = slot[mid]
        if page >= 13:
            boss += 1  # fiends/Chaos: use find_ff1_monster_tiles + colorize_monster
            continue
        off, w, h = GFX_SLOT[gfx]
        rgb = palettes[mid][1]
        img = render_sprite(data, page_base(page) + off, w, h, rgb)
        safe = names[mid].replace('/', '_').replace(' ', '_')
        img.resize((w * 8 * 3, h * 8 * 3), Image.NEAREST).save(
            os.path.join(out_dir, f"{mid:03d}_{safe}.png"))
        done += 1

    print(f"wrote {done} colored monster sprites to {out_dir}")
    print(f"({boss} fiend/Chaos sprites use colorize_monster.py; {skipped} unused ids)")


if __name__ == "__main__":
    main()
