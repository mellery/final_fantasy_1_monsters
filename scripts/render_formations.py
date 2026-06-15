"""Render each enemy formation as a battle scene - monsters placed at their real
on-screen positions, on the black battle background.

Slot positions and sizes come from the battle code (bank_0B/0C):
  * 9-Small (type 0): up to 9 small (32x32) enemies in a 3x3 grid; positions from
    lut_ExplosionCoords_9Small.
  * 4-Large (type 1): up to 4 large (48x48) enemies in a 2x2 grid;
    lut_ExplosionCoords_4Large.
  * Mix (type 2): up to 2 large (left column) + 6 small (right two columns);
    lut_EraseEnemyPPUAddress_4Large / _Mix_Small.
  * Fiend/Chaos (type 3/4): a single large boss sprite, centred.

Each formation lists up to 4 groups (enemy id + quantity + a 2-bit gfx field whose
low bit is size: 0 small, 1 large). Slots fill in group order using the group's
MAX quantity. Enemy sprites are rendered natively (extract_monster_sprites) in the
monster's battle palette.

Writes output/formations/NNN.png (NNN = formation id), only for non-empty
formations.
"""
import os
import sys
from PIL import Image
from monster_names import get_names
from ff1_palettes import get_monster_palettes
from extract_monster_sprites import (render_grid, render_boss, GFX_SLOT,
                                     BOSS_SPRITES, FORMATIONS)

# pixel (x, y) top-left of each slot, in fill order
POS_9SMALL = [(16, 80), (16, 48), (16, 112), (48, 80), (48, 48), (48, 112),
              (80, 80), (80, 48), (80, 112)]
POS_4LARGE = [(16, 48), (16, 96), (80, 48), (80, 96)]
POS_MIX_LARGE = [(16, 48), (16, 96)]
POS_MIX_SMALL = [(64, 80), (64, 48), (64, 112), (96, 80), (96, 48), (96, 112)]

CANVAS = (128, 144)
SCALE = 3


def monster_img(data, eid, page, gfx, palettes, names):
    """Native-size RGB battle sprite for one enemy id."""
    rgb = palettes.get(eid, (None, [(0, 0, 0)] * 4, None))[1]
    name = names[eid]
    if name in BOSS_SPRITES:
        base, cols, rows, blanks = BOSS_SPRITES[name]
        return render_boss(data, base, cols, rows, blanks, rgb)
    off, w, h = GFX_SLOT[gfx]
    base = (0x1c000 + page * 0x800 if page < 8 else 0x20000 + (page - 8) * 0x800) + off
    return render_grid(data, base, w, h, rgb)


def render_formation(data, fid, palettes, names):
    e = data[FORMATIONS + fid * 16: FORMATIONS + fid * 16 + 16]
    ftype = e[0] >> 4
    page = e[0] & 0x0f
    groups = []
    for s in range(4):
        eid, qmax = e[2 + s], e[6 + s] & 0x0f
        gfx = (e[1] >> (2 * s)) & 3
        if eid < 0x80 and qmax > 0:
            groups.append((eid, qmax, gfx))
    if not groups:
        return None

    scene = Image.new('RGB', CANVAS)  # black

    if ftype >= 3:  # fiend / chaos: single centred boss
        eid = groups[0][0]
        spr = monster_img(data, eid, page, groups[0][2], palettes, names)
        scene.paste(spr, ((CANVAS[0] - spr.width) // 2,
                          max(0, (CANVAS[1] - spr.height) // 2)))
        return scene.resize((CANVAS[0] * SCALE, CANVAS[1] * SCALE), Image.NEAREST)

    if ftype == 1:
        large_pos, small_pos = list(POS_4LARGE), []
    elif ftype == 2:
        large_pos, small_pos = list(POS_MIX_LARGE), list(POS_MIX_SMALL)
    else:  # 0 = 9 small
        large_pos, small_pos = [], list(POS_9SMALL)

    for eid, qmax, gfx in groups:
        is_large = gfx & 1
        pool = large_pos if is_large else small_pos
        spr = monster_img(data, eid, page, gfx, palettes, names)
        for _ in range(qmax):
            if not pool:
                break
            x, y = pool.pop(0)
            scene.paste(spr, (x, y))
    return scene.resize((CANVAS[0] * SCALE, CANVAS[1] * SCALE), Image.NEAREST)


def main():
    rom = sys.argv[1] if len(sys.argv) > 1 else '../roms/Final Fantasy (USA).nes'
    out_dir = sys.argv[2] if len(sys.argv) > 2 else '../output/formations'
    with open(rom, 'rb') as f:
        data = f.read()
    os.makedirs(out_dir, exist_ok=True)
    names = get_names(data)
    palettes = get_monster_palettes(data)
    n = 0
    for fid in range(128):
        img = render_formation(data, fid, palettes, names)
        if img is not None:
            img.save(os.path.join(out_dir, f"{fid:03d}.png"))
            n += 1
    print(f"wrote {n} formation battle scenes to {out_dir}")


if __name__ == "__main__":
    main()
