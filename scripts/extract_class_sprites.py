"""Extract the 6 character-class mapman (overworld) sprites in color.

The player mapman CHR is per class (LoadPlayerMapmanCHR): bank 02, source
$9000 + class*0x100 = file 0x9010 + class*0x100, 16 tiles. The standing
(down-facing) frame is tiles 0,1,2,3 (TL,TR,BL,BR) - same 2x2 layout as map
objects (Draw2x2Sprite). Class colors come from lut_MapmanPalettes (file 0x3b0,
2 NES colors per class).

Writes output/classes/N_Name.png (transparent background).
"""
import os
import sys
import numpy as np
from PIL import Image
from nes_color_converter import NES_PALETTE

MAPMAN_CHR, MAPMAN_PAL = 0x9010, 0x3b0
CLASS_NAMES = ['Fighter', 'Thief', 'BlackBelt', 'RedMage', 'WhiteMage', 'BlackMage']


def tile(data, off):
    t = np.zeros((8, 8), int)
    for y in range(8):
        lo, hi = data[off + y], data[off + y + 8]
        for x in range(8):
            t[y, x] = ((lo >> (7 - x)) & 1) | (((hi >> (7 - x)) & 1) << 1)
    return t


def class_sprite(data, cls):
    a, b = data[MAPMAN_PAL + cls * 2] & 0x3f, data[MAPMAN_PAL + cls * 2 + 1] & 0x3f
    pal = [None, NES_PALETTE[0x30], NES_PALETTE[a], NES_PALETTE[b]]  # 0 = transparent
    base = MAPMAN_CHR + cls * 0x100
    img = Image.new('RGBA', (16, 16))
    px = img.load()
    for qi, ti in enumerate((0, 1, 2, 3)):
        t = tile(data, base + ti * 16)
        ox, oy = (qi % 2) * 8, (qi // 2) * 8
        for y in range(8):
            for x in range(8):
                if t[y, x]:
                    px[ox + x, oy + y] = pal[t[y, x]] + (255,)
    return img


def main():
    rom = sys.argv[1] if len(sys.argv) > 1 else '../roms/Final Fantasy (USA).nes'
    out_dir = sys.argv[2] if len(sys.argv) > 2 else '../output/classes'
    with open(rom, 'rb') as f:
        data = f.read()
    os.makedirs(out_dir, exist_ok=True)
    for c, name in enumerate(CLASS_NAMES):
        img = class_sprite(data, c)
        img.resize((64, 64), Image.NEAREST).save(os.path.join(out_dir, f"{c}_{name}.png"))
    print(f"wrote {len(CLASS_NAMES)} class sprites to {out_dir}")


if __name__ == "__main__":
    main()
