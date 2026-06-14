"""Render Final Fantasy (USA) standard maps (towns, castles, dungeons) to PNG.

Pipeline (offsets from the FF1 disassembly, bank_0F.asm):
  map id -> tileset      : lut_Tilesets, file 0x2cd0 + map
  map id -> compressed   : lut_SMPtrTbl (bank 04 $8000 = file 0x10010); the
                           2-byte entry is an offset, so data = 0x10010 + ptr
  RLE: byte 0x00-0x7f = one metatile; 0x80-0xfe = run (tile = b&0x7f, next
       byte = count, 0 -> 256); 0xff = end. Maps are 64x64 metatiles.
  metatile -> 4 CHR tiles: tsa_ul/ur/dl/dr, 512 bytes/tileset at 0x1010+ts*512
                           (four 128-byte arrays)
  metatile -> palette    : tsa_attr (low 2 bits), 128 bytes/tileset at 0x410+ts*128
  tileset CHR            : 0xc010 + ts*0x800 (bank 03), 128 tiles
  map palette            : lut_SMPalettes, 0x2010 + map*0x30 (first 16 bytes =
                           4 BG palettes x 4 NES colors)
A metatile is 16x16 px (2x2 CHR tiles of 8x8); a map renders to 1024x1024.
"""
import os
import struct
import sys
import numpy as np
from PIL import Image
from nes_color_converter import NES_PALETTE
from print_domains import MAP_NAMES

SMPTR, TILESETS, TSA, ATTR, CHRBASE, PAL = 0x10010, 0x2cd0, 0x1010, 0x410, 0xc010, 0x2010
MAP_W = MAP_H = 64


def decompress(data, src):
    out = []
    i = src
    while len(out) < MAP_W * MAP_H:
        b = data[i]; i += 1
        if b == 0xff:
            break
        if b & 0x80:
            t = b & 0x7f
            c = data[i]; i += 1
            out += [t] * (c or 256)
        else:
            out.append(b)
    return (out + [0] * (MAP_W * MAP_H))[:MAP_W * MAP_H]


def tile_pixels(data, chr_base, cid):
    t = np.zeros((8, 8), int)
    o = chr_base + cid * 16
    for y in range(8):
        lo, hi = data[o + y], data[o + y + 8]
        for x in range(8):
            t[y, x] = ((lo >> (7 - x)) & 1) | (((hi >> (7 - x)) & 1) << 1)
    return t


def render_map(data, mapid):
    ts = data[TILESETS + mapid]
    ptr = struct.unpack_from('<H', data, SMPTR + mapid * 2)[0]
    grid = decompress(data, SMPTR + ptr)
    tb, ab, cb = TSA + ts * 512, ATTR + ts * 128, CHRBASE + ts * 0x800
    po = PAL + mapid * 0x30
    pals = [[NES_PALETTE[data[po + p * 4 + c] & 0x3f] for c in range(4)] for p in range(4)]
    img = Image.new('RGB', (MAP_W * 16, MAP_H * 16))
    px = img.load()
    tilecache = {}
    for my in range(MAP_H):
        for mx in range(MAP_W):
            m = grid[my * MAP_W + mx]
            pal = pals[data[ab + m] & 3]
            for qi, cid in enumerate(((data[tb + m], data[tb + 128 + m],
                                       data[tb + 256 + m], data[tb + 384 + m]))):
                t = tilecache.get(cid)
                if t is None:
                    t = tilecache.setdefault(cid, tile_pixels(data, cb, cid))
                ox, oy = mx * 16 + (qi % 2) * 8, my * 16 + (qi // 2) * 8
                for y in range(8):
                    for x in range(8):
                        px[ox + x, oy + y] = pal[t[y, x]]
    return img


def main():
    rom = sys.argv[1] if len(sys.argv) > 1 else '../roms/Final Fantasy (USA).nes'
    out_dir = sys.argv[2] if len(sys.argv) > 2 else '../output/maps'
    with open(rom, 'rb') as f:
        data = f.read()
    os.makedirs(out_dir, exist_ok=True)
    for mapid in range(61):
        name = MAP_NAMES.get(mapid, f'map{mapid}').replace('/', '_').replace(' ', '_')
        render_map(data, mapid).save(os.path.join(out_dir, f"{mapid:02d}_{name}.png"))
    print(f"rendered 61 standard maps to {out_dir}")


if __name__ == "__main__":
    main()
