"""Map monsters to their sprite CHR page and palette (Final Fantasy USA).

Each battle loads one enemy CHR "page" = the low nibble of the formation's
byte 0 (bank_0F.asm line 10023-10026). A page holds the sprite graphics shared
by all monsters that appear in formations using it - which is why palette-swap
pairs (IMP/GrIMP, the dragons) and themed groups land on the same page.

CHR page -> ROM offset (from LoadBattleBGCHRPointers, bank_0F.asm 10055):
  page 0-7 : 0x1c010 + page*0x800      (BANK_BATTLECHR = 0x07)
  page 8-15: 0x20010 + (page-8)*0x800  (BANK_BATTLECHR+1)
Each page is 0x800 bytes (128 tiles): row 0 is the battle backdrop, the rest
holds 2 enemy images (image 0 / image 1), 4x4 tiles for small enemies or 6x6
for large.

This script reports, per CHR page, the monsters that share it and each one's
battle palette (see ff1_palettes.py). It is the verified monster<->sprite-set
grouping; pixel-perfect per-monster extraction additionally needs the image-0/1
split and size per monster (a fuller sprite-extractor task).
"""
import sys
from collections import defaultdict
from monster_names import get_names
from ff1_palettes import get_monster_palettes

FORMATIONS = 0x2c410


def chr_page_rom(page):
    if page < 8:
        return 0x1c010 + page * 0x800
    return 0x20010 + (page - 8) * 0x800


def main():
    rom = sys.argv[1] if len(sys.argv) > 1 else '../roms/Final Fantasy (USA).nes'
    try:
        with open(rom, 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        print(f"Error: ROM file '{rom}' not found")
        sys.exit(1)

    names = get_names(data)
    palettes = get_monster_palettes(data)

    # monster -> CHR page, via the first formation that uses it
    page_of = {}
    for f in range(128):
        e = data[FORMATIONS + f * 16: FORMATIONS + f * 16 + 16]
        for s in range(4):
            eid = e[2 + s]
            if eid < 0x80 and (e[6 + s] & 0x0f) > 0 and eid not in page_of:
                page_of[eid] = e[0] & 0x0f

    by_page = defaultdict(list)
    for mid, pg in page_of.items():
        by_page[pg].append(mid)

    for pg in sorted(by_page):
        print(f"\nCHR page {pg:2d}  (ROM 0x{chr_page_rom(pg):05x})")
        for mid in sorted(by_page[pg]):
            pid, rgb, _ = palettes.get(mid, (None, [], None))
            cols = ' '.join(f"#{r:02x}{g:02x}{b:02x}" for r, g, b in rgb)
            pal = f"pal{pid:2d}: {cols}" if pid is not None else "(no palette)"
            print(f"    {names[mid]:9s}  {pal}")


if __name__ == "__main__":
    main()
