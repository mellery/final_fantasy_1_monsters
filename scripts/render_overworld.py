"""Render the Final Fantasy (USA) overworld map to PNG (plain + annotated).

The overworld is 256x256 metatiles, each row RLE-compressed (same scheme as
standard maps). Row pointer table: lut_OWPtrTbl at bank 01 $8000 (file 0x4010).
OW tileset is a 0x400 block at file 0x10: +0x000 tile properties (2/metatile),
+0x100/180/200/280 TSA ul/ur/dl/dr, +0x300 attr, +0x380 palette. OW BG CHR at
file 0x8010 (bank 02). Each metatile is 16x16 px; full map = 4096x4096.

The annotated map adds:
  * the 8x8 encounter-zone grid (domain = (Y>>5)*8 + (X>>5)), each cell labeled
    with its zone number and a representative monster (from the battle domains)
  * entrance markers: OW tiles with a teleport property (prop 2nd byte >= 0x80)
    labeled with their destination map (lut_EntrTele_Map at file 0x2c50)
"""
import os
import struct
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from nes_color_converter import NES_PALETTE
from monster_names import get_names
from print_domains import MAP_NAMES

OWPTR, OWPROP, TSA_UL, ATTR, OWPAL, OWCHR = 0x4010, 0x10, 0x110, 0x310, 0x390, 0x8010
DOMAINS, FORMATIONS, ENTR_MAP = 0x2c010, 0x2c410, 0x2c50
SIZE = 256


def _font(sz):
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", sz)
    except Exception:
        return ImageFont.load_default()


def decompress_grid(data):
    def row(src):
        out, i = [], src
        while len(out) < SIZE:
            b = data[i]; i += 1
            if b == 0xff:
                break
            if b & 0x80:
                c = data[i]; i += 1
                out += [b & 0x7f] * (c or 256)
            else:
                out.append(b)
        return (out + [0] * SIZE)[:SIZE]
    return [row(0x4010 + (struct.unpack_from('<H', data, OWPTR + r * 2)[0] - 0x8000))
            for r in range(SIZE)]


def render(data, grid):
    pals = [[NES_PALETTE[data[OWPAL + p * 4 + c] & 0x3f] for c in range(4)] for p in range(4)]
    tcache = {}

    def tile(c):
        t = tcache.get(c)
        if t is None:
            t = np.zeros((8, 8), int)
            o = OWCHR + c * 16
            for y in range(8):
                lo, hi = data[o + y], data[o + y + 8]
                for x in range(8):
                    t[y, x] = ((lo >> (7 - x)) & 1) | (((hi >> (7 - x)) & 1) << 1)
            tcache[c] = t
        return t

    img = Image.new('RGB', (SIZE * 16, SIZE * 16))
    px = img.load()
    for my in range(SIZE):
        for mx in range(SIZE):
            m = grid[my][mx]
            pal = pals[data[ATTR + m] & 3]
            for qi, cid in enumerate((data[TSA_UL + m], data[TSA_UL + 128 + m],
                                      data[TSA_UL + 256 + m], data[TSA_UL + 384 + m])):
                t = tile(cid)
                ox, oy = mx * 16 + (qi % 2) * 8, my * 16 + (qi // 2) * 8
                for y in range(8):
                    for x in range(8):
                        px[ox + x, oy + y] = pal[t[y, x]]
    return img


def domain_monster(data, names, d):
    """A representative monster for OW zone d (first non-empty formation it rolls)."""
    for ref in data[DOMAINS + d * 8: DOMAINS + d * 8 + 8]:
        e = data[FORMATIONS + (ref & 0x7f) * 16: FORMATIONS + (ref & 0x7f) * 16 + 16]
        for s in range(4):
            eid = e[2 + s]
            if eid < 0x80 and (e[6 + s] & 0x0f) > 0:
                return names[eid] if eid < len(names) else f'#{eid}'
    return ''


def annotate(img, data, grid):
    d = ImageDraw.Draw(img)
    names = get_names(data)
    zfont, efont = _font(30), _font(26)

    # 8x8 encounter-zone grid (each cell = 32x32 tiles = 512 px)
    for i in range(9):
        d.line([(i * 512, 0), (i * 512, SIZE * 16)], fill=(255, 255, 0), width=2)
        d.line([(0, i * 512), (SIZE * 16, i * 512)], fill=(255, 255, 0), width=2)
    for row in range(8):
        for col in range(8):
            zone = row * 8 + col
            mon = domain_monster(data, names, zone)
            label = f"Z{zone}\n{mon}" if mon else f"Z{zone}"
            d.multiline_text((col * 512 + 6, row * 512 + 4), label,
                             fill=(255, 255, 0), font=zfont,
                             stroke_width=3, stroke_fill=(0, 0, 0))

    # entrances: OW tiles whose 2nd property byte has the teleport bit
    seen = {}
    for y in range(SIZE):
        for x in range(SIZE):
            p = data[OWPROP + grid[y][x] * 2 + 1]
            if p & 0x80:
                tid = p & 0x7f
                if tid not in seen:
                    seen[tid] = (x, y)
    for tid, (x, y) in seen.items():
        name = MAP_NAMES.get(data[ENTR_MAP + tid], f'map{data[ENTR_MAP + tid]}')
        px0, py0 = x * 16, y * 16
        d.rectangle([px0 - 2, py0 - 2, px0 + 17, py0 + 17], outline=(255, 60, 60), width=3)
        d.text((px0 + 20, py0), name, fill=(255, 255, 255), font=efont,
               stroke_width=3, stroke_fill=(0, 0, 0))
    return img


def main():
    rom = sys.argv[1] if len(sys.argv) > 1 else '../roms/Final Fantasy (USA).nes'
    out_dir = sys.argv[2] if len(sys.argv) > 2 else '../output/maps'
    with open(rom, 'rb') as f:
        data = f.read()
    os.makedirs(out_dir, exist_ok=True)

    grid = decompress_grid(data)
    img = render(data, grid)
    img.save(os.path.join(out_dir, 'overworld.png'))
    img.resize((1024, 1024), Image.NEAREST).save(os.path.join(out_dir, 'overworld_preview.png'))

    ann = annotate(img.copy(), data, grid)
    ann.save(os.path.join(out_dir, 'overworld_annotated.png'))
    ann.resize((1536, 1536), Image.LANCZOS).save(os.path.join(out_dir, 'overworld_annotated_preview.png'))
    print(f"rendered overworld (plain + annotated, 4096x4096) + previews to {out_dir}")


if __name__ == "__main__":
    main()
