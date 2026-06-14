"""Extract every monster sprite in color from Final Fantasy (USA).

Regular monsters map to a sprite slot via their formations:
  CHR page   = formation byte 0 low nibble (which 0x800 CHR page is loaded)
  gfx (0-3)  = (formation byte 1 >> (2*slot)) & 3, where bit0 = size
               (0 = small 4x4, 1 = medium 6x6) and bit1 = image (0 or 1)
CHR page -> ROM base:  page 0-7 at 0x1c000 + page*0x800,
                       page 8-12 at 0x20000 + (page-8)*0x800.
Sprite offsets within a page (verified visually):
  gfx 0 (small img0) +0x130   gfx 2 (small img1) +0x230
  gfx 1 (med   img0) +0x330   gfx 3 (med   img1) +0x570

The fiends and Chaos (monster ids 119-127) use a tile-arrangement (TSA) layout
instead - a fixed grid with blanked cells, the non-blank cells filled from
consecutive ROM tiles (ported from find_ff1_monster_tiles.py).

Tiles are colored with the monster's battle palette (ff1_palettes). Background
is black (palette color 0), matching the game's battle screen.
"""
import os
import sys
import numpy as np
from PIL import Image
from monster_names import get_names
from ff1_palettes import get_monster_palettes

FORMATIONS = 0x2c410
GFX_SLOT = {0: (0x130, 4, 4), 2: (0x230, 4, 4), 1: (0x330, 6, 6), 3: (0x570, 6, 6)}

# Fiend/Chaos sprites: name -> (rom_start, cols, rows, set-of-blank-cell-indices)
BOSS_SPRITES = {
    'LICH':   (0x22c90, 8, 8, {4, 5, 6, 7, 14, 15, 23, 31, 38, 39, 47, 54, 55, 63}),
    'KARY':   (0x22920, 8, 8, {15, 39, 47, 48, 49, 55, 56, 57, 58, 63}),
    'KRAKEN': (0x23120, 8, 8, {0, 6, 7, 8, 15, 16, 24, 32, 48, 56, 58}),
    'TIAMAT': (0x23470, 8, 8, {0, 1, 2, 6, 7, 15, 23, 31, 39, 48, 56, 63}),
    'CHAOS':  (0x23920, 14, 12, {0, 1, 5, 10, 11, 12, 13, 14, 15, 25, 26, 27, 28,
                                 40, 41, 42, 55, 69, 80, 85, 86, 93, 94, 95, 96,
                                 98, 99, 100, 108, 109, 110, 111, 112, 113, 114,
                                 118, 122, 123, 124, 125, 126, 127, 136, 137, 138,
                                 139, 140, 141, 145, 146, 147, 150, 151, 152, 153,
                                 154, 155, 156, 157, 158, 159, 160, 161}),
}


def decode_tile(data, off):
    t = np.zeros((8, 8), int)
    for i in range(8):
        lo, hi = data[off + i], data[off + i + 8]
        for j in range(8):
            t[i, j] = ((lo >> (7 - j)) & 1) | (((hi >> (7 - j)) & 1) << 1)
    return t


def paste_tile(px, t, ox, oy, palette):
    for y in range(8):
        for x in range(8):
            px[ox + x, oy + y] = palette[t[y, x]]  # value 0 = palette[0] = black


def render_grid(data, base, w, h, palette):
    """w*h consecutive tiles, colored. Black background (value 0)."""
    img = Image.new('RGB', (w * 8, h * 8))
    px = img.load()
    for n in range(w * h):
        paste_tile(px, decode_tile(data, base + n * 16), (n % w) * 8, (n // w) * 8, palette)
    return img


def render_boss(data, base, cols, rows, blanks, palette):
    """Grid with blank cells; non-blank cells use consecutive ROM tiles."""
    img = Image.new('RGB', (cols * 8, rows * 8))
    px = img.load()
    src = 0
    for p in range(cols * rows):
        if p in blanks:
            continue  # leave black
        paste_tile(px, decode_tile(data, base + src * 16), (p % cols) * 8, (p // cols) * 8, palette)
        src += 1
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

    slot = {}
    for f in range(128):
        e = data[FORMATIONS + f * 16: FORMATIONS + f * 16 + 16]
        for s in range(4):
            eid = e[2 + s]
            if eid < 0x80 and (e[6 + s] & 0x0f) > 0 and eid not in slot:
                slot[eid] = (e[0] & 0x0f, (e[1] >> (2 * s)) & 3)

    written = skipped = 0
    for mid in range(128):
        if mid not in palettes:
            skipped += 1
            continue
        rgb = palettes[mid][1]
        name = names[mid]
        if name in BOSS_SPRITES:
            base, cols, rows, blanks = BOSS_SPRITES[name]
            img = render_boss(data, base, cols, rows, blanks, rgb)
        elif mid in slot and (slot[mid][0]) < 13:
            page, gfx = slot[mid]
            off, w, h = GFX_SLOT[gfx]
            img = render_grid(data, (0x1c000 + page * 0x800 if page < 8
                                     else 0x20000 + (page - 8) * 0x800) + off, w, h, rgb)
        else:
            skipped += 1
            continue
        safe = name.replace('/', '_').replace(' ', '_')
        img.resize((img.width * 3, img.height * 3), Image.NEAREST).save(
            os.path.join(out_dir, f"{mid:03d}_{safe}.png"))
        written += 1

    print(f"wrote {written} colored monster sprites to {out_dir} ({skipped} unused ids)")


if __name__ == "__main__":
    main()
