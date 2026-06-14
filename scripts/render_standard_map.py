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
from PIL import Image, ImageDraw, ImageFont
from nes_color_converter import NES_PALETTE
from print_domains import MAP_NAMES

SMPTR, TILESETS, TSA, ATTR, CHRBASE, PAL = 0x10010, 0x2cd0, 0x1010, 0x410, 0xc010, 0x2010
PROP, MAPOBJ, TREASURE = 0x810, 0x3410, 0x3f110
MAP_W = MAP_H = 64

try:
    _FONT = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 11)
except Exception:
    _FONT = ImageFont.load_default()


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


def find_chests(data, mapid):
    """Chest tiles: tileset_prop ssss field == 4. Returns (mx, my, treasure_id)."""
    ts = data[TILESETS + mapid]
    pb = PROP + ts * 256
    chest_tiles = {m: data[pb + m * 2 + 1] for m in range(128)
                   if (data[pb + m * 2] >> 1) & 0x0f == 4}
    grid = decompress(data, SMPTR + struct.unpack_from('<H', data, SMPTR + mapid * 2)[0])
    return [(i % MAP_W, i // MAP_W, chest_tiles[m])
            for i, m in enumerate(grid) if m in chest_tiles]


def find_npcs(data, mapid):
    """16 map objects x (id, X-with-flags, Y). Returns (id, mx, my) for real ones."""
    o = MAPOBJ + mapid * 0x30
    out = []
    for k in range(16):
        oid, x, y = data[o + k * 3], data[o + k * 3 + 1], data[o + k * 3 + 2]
        if oid:
            out.append((oid, x & 0x3f, y & 0x3f))
    return out


def annotate(img, data, mapid, item_name):
    """Overlay chest (yellow, labeled with contents) and NPC (cyan) markers."""
    d = ImageDraw.Draw(img)
    for mx, my, tid in find_chests(data, mapid):
        x, y = mx * 16, my * 16
        d.rectangle([x, y, x + 15, y + 15], outline=(255, 230, 0), width=2)
        d.text((x + 1, y + 16), item_name(data[TREASURE + tid]), fill=(255, 230, 0), font=_FONT)
    for oid, mx, my in find_npcs(data, mapid):
        x, y = mx * 16, my * 16
        d.rectangle([x, y, x + 15, y + 15], outline=(0, 230, 255), width=2)
        d.text((x + 2, y + 2), str(oid), fill=(0, 230, 255), font=_FONT)
    return img


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    list_only = '--list' in sys.argv
    rom = args[0] if args else '../roms/Final Fantasy (USA).nes'
    out_dir = args[1] if len(args) > 1 else '../output/maps'
    with open(rom, 'rb') as f:
        data = f.read()

    from item_names import build_item_id_map, get_gold_names
    id_map = build_item_id_map(data)
    gold = get_gold_names(data)

    def item_name(iid):
        # Treasure namespace: 0x01-0x6b items, 0x6c-0xaf gold, 0xb0+ higher gold
        # (not yet decoded). NOTE: 0xb0+ is NOT magic here - that's the shop namespace.
        if iid <= 0x6b and iid in id_map:
            return id_map[iid]
        if 0x6c <= iid < 0x6c + len(gold):
            return gold[iid - 0x6c]
        return f'gold?:{iid:02x}'

    if list_only:
        # Text dump of chests/NPCs per map, for verifying contents against a guide
        for mapid in range(61):
            name = MAP_NAMES.get(mapid, f'map{mapid}')
            chests = find_chests(data, mapid)
            npcs = find_npcs(data, mapid)
            print(f"\n[{mapid:02d}] {name}  ({len(chests)} chests, {len(npcs)} NPCs)")
            seen = set()
            for mx, my, tid in chests:
                if tid in seen:
                    continue
                seen.add(tid)
                print(f"    chest @({mx:2d},{my:2d}) TC{tid:<3d} = {item_name(data[TREASURE + tid])}")
        return

    os.makedirs(out_dir, exist_ok=True)
    for mapid in range(61):
        name = MAP_NAMES.get(mapid, f'map{mapid}').replace('/', '_').replace(' ', '_')
        base = render_map(data, mapid)
        base.save(os.path.join(out_dir, f"{mapid:02d}_{name}.png"))
        annotate(base.copy(), data, mapid, item_name).save(
            os.path.join(out_dir, f"{mapid:02d}_{name}_annotated.png"))
    print(f"rendered 61 standard maps (plain + annotated) to {out_dir}")


if __name__ == "__main__":
    main()
