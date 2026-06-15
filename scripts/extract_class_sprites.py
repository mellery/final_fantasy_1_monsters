"""Extract the 6 character-class sprites in pixel-exact color: both the overworld
'mapman' sprite and the battle sprite.

MAPMAN (overworld walking figure), per DrawPlayerMapmanSprite / Draw2x2Sprite:
  CHR  : LoadPlayerMapmanCHR, bank 02, $9000 + class*0x100 = file 0x9010+class*0x100.
  The standing/facing-down frame (lut_PlayerMapmanSprTbl) is tiles 0,1 (top row,
  sprite palette 0) and 2,3 (bottom row, sprite palette 1).
  Palette: the overworld base sprite palettes (file 0x3a0) are
     pal0 = 0f,0f,12,36   pal1 = 0f,0f,27,36
  and SetMapmanPalette overwrites color index 2 of each with the class colors from
  lut_MapmanPalettes (file 0x3b0, 2 bytes/class): pal0[2]=classA, pal1[2]=classB.
  Sprite color index 0 is transparent.

BATTLE (the standing combat figure), per DrawCharacter / DrawSimple2x3Sprite:
  CHR  : lut_BatSprCHR, bank 09, file 0x25010 + class*0x200 (2 rows = 32 tiles).
  The standing pose (lut_CharacterPoseTSA, CHARPOSE_STAND = 00,02,04) is a 2x3
  arrangement: tiles 0,1 / 2,3 / 4,5 (16x24 px).
  Palette: lutClassBatSprPalette (file 0x3b1d-ish) picks attribute 0 or 1 ->
     [01,00,00,01,01,00] for the 6 unpromoted classes. The two battle sprite
  palettes (LoadBattleSpritePalettes) are pal0 = 0f,28,18,21, pal1 = 0f,16,30,36.
  Color index 0 is transparent.

Writes output/classes/N_Name.png (mapman) and N_Name_battle.png (battle).
"""
import os
import sys
import numpy as np
from PIL import Image
from nes_color_converter import NES_PALETTE

MAPMAN_CHR = 0x9010          # bank 02, $9000
OW_SPR_PAL = 0x3a0           # 4 overworld sprite palettes x 4 bytes
MAPMAN_PAL = 0x3b0           # lut_MapmanPalettes, 2 bytes/class
BATSPR_CHR = 0x25010         # lut_BatSprCHR, bank 09
# lutClassBatSprPalette ($ECB4): attribute byte per class -> sprite palette 0/1
CLASS_BAT_PAL_IDX = [0x01, 0x00, 0x00, 0x01, 0x01, 0x00]
# LoadBattleSpritePalettes: 4 sprite palettes (only 0 and 1 used by classes)
BAT_SPR_PAL = [0x0f, 0x28, 0x18, 0x21,  0x0f, 0x16, 0x30, 0x36,
               0x0f, 0x30, 0x22, 0x12,  0x0f, 0x30, 0x10, 0x00]
CLASS_NAMES = ['Fighter', 'Thief', 'BlackBelt', 'RedMage', 'WhiteMage', 'BlackMage']


def tile(data, off):
    t = np.zeros((8, 8), int)
    for y in range(8):
        lo, hi = data[off + y], data[off + y + 8]
        for x in range(8):
            t[y, x] = ((lo >> (7 - x)) & 1) | (((hi >> (7 - x)) & 1) << 1)
    return t


def _rgba(idx):
    return NES_PALETTE[idx & 0x3f] + (255,)


def paste(img, data, off, ox, oy, pal):
    """Paste an 8x8 tile; pal is 4 entries, None = transparent."""
    px = img.load()
    t = tile(data, off)
    for y in range(8):
        for x in range(8):
            c = pal[t[y, x]]
            if c is not None:
                px[ox + x, oy + y] = c


def mapman_sprite(data, cls):
    a = data[MAPMAN_PAL + cls * 2] & 0x3f       # class color for sprite palette 0
    b = data[MAPMAN_PAL + cls * 2 + 1] & 0x3f   # class color for sprite palette 1
    p0 = list(data[OW_SPR_PAL: OW_SPR_PAL + 4])
    p1 = list(data[OW_SPR_PAL + 4: OW_SPR_PAL + 8])
    p0[2], p1[2] = a, b
    pal0 = [None] + [_rgba(c) for c in p0[1:]]   # index 0 transparent
    pal1 = [None] + [_rgba(c) for c in p1[1:]]
    base = MAPMAN_CHR + cls * 0x100
    img = Image.new('RGBA', (16, 16))
    paste(img, data, base + 0 * 16, 0, 0, pal0)   # top row -> sprite palette 0
    paste(img, data, base + 1 * 16, 8, 0, pal0)
    paste(img, data, base + 2 * 16, 0, 8, pal1)   # bottom row -> sprite palette 1
    paste(img, data, base + 3 * 16, 8, 8, pal1)
    return img


def battle_sprite(data, cls):
    pi = CLASS_BAT_PAL_IDX[cls] * 4
    pal = [None] + [_rgba(c) for c in BAT_SPR_PAL[pi + 1: pi + 4]]
    base = BATSPR_CHR + cls * 0x200
    img = Image.new('RGBA', (16, 24))
    for row, t in enumerate((0, 2, 4)):           # rows: tiles 0,1 / 2,3 / 4,5
        paste(img, data, base + t * 16, 0, row * 8, pal)
        paste(img, data, base + (t + 1) * 16, 8, row * 8, pal)
    return img


def main():
    rom = sys.argv[1] if len(sys.argv) > 1 else '../roms/Final Fantasy (USA).nes'
    out_dir = sys.argv[2] if len(sys.argv) > 2 else '../output/classes'
    with open(rom, 'rb') as f:
        data = f.read()
    os.makedirs(out_dir, exist_ok=True)
    for c, name in enumerate(CLASS_NAMES):
        mapman_sprite(data, c).resize((64, 64), Image.NEAREST).save(
            os.path.join(out_dir, f"{c}_{name}.png"))
        battle_sprite(data, c).resize((64, 96), Image.NEAREST).save(
            os.path.join(out_dir, f"{c}_{name}_battle.png"))
    print(f"wrote {len(CLASS_NAMES)} mapman + battle class sprites to {out_dir}")


if __name__ == "__main__":
    main()
