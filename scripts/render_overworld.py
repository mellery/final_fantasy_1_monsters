"""Render the Final Fantasy (USA) overworld map to PNG.

The overworld is 256x256 metatiles, each row RLE-compressed (same scheme as
standard maps - see render_standard_map.py). Row pointer table: lut_OWPtrTbl at
bank 01 $8000 (file 0x4010), 256 little-endian CPU pointers; row R data is at
file 0x4010 + (ptr - 0x8000).

The overworld tileset is a single 0x400 block at file 0x10 (lut_OWTileset,
bank 00 $8000):
  +0x000 tile properties (256 bytes, 2/metatile)
  +0x100/+0x180/+0x200/+0x280 TSA: ul/ur/dl/dr CHR tile ids (128 each)
  +0x300 attribute (palette select, low 2 bits), 128 bytes
  +0x380 palette: 4 BG palettes x 4 NES colors (16 bytes)
OW background CHR: bank 02 $8000 (file 0x8010), 256 tiles.

Each metatile is 16x16 px (2x2 CHR tiles); the full map renders to 4096x4096.
"""
import os
import struct
import sys
import numpy as np
from PIL import Image
from nes_color_converter import NES_PALETTE

OWPTR, TSA_UL, ATTR, OWPAL, OWCHR = 0x4010, 0x110, 0x310, 0x390, 0x8010
SIZE = 256


def decompress_row(data, src):
    out = []
    i = src
    while len(out) < SIZE:
        b = data[i]; i += 1
        if b == 0xff:
            break
        if b & 0x80:
            t = b & 0x7f
            c = data[i]; i += 1
            out += [t] * (c or 256)
        else:
            out.append(b)
    return (out + [0] * SIZE)[:SIZE]


def main():
    rom = sys.argv[1] if len(sys.argv) > 1 else '../roms/Final Fantasy (USA).nes'
    out_dir = sys.argv[2] if len(sys.argv) > 2 else '../output/maps'
    with open(rom, 'rb') as f:
        data = f.read()
    os.makedirs(out_dir, exist_ok=True)

    grid = [decompress_row(data, 0x4010 + (struct.unpack_from('<H', data, OWPTR + r * 2)[0] - 0x8000))
            for r in range(SIZE)]
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

    img.save(os.path.join(out_dir, 'overworld.png'))
    img.resize((1024, 1024), Image.NEAREST).save(os.path.join(out_dir, 'overworld_preview.png'))
    print(f"rendered overworld (4096x4096) + preview to {out_dir}")


if __name__ == "__main__":
    main()
