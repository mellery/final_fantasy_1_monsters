"""Colorize a grayscale FF1 monster sprite using the monster's battle palette.

The grayscale sprites from find_ff1_monster_tiles.py use pixel levels
0/85/170/255 for the 4 tile color values. This maps those to the monster's
palette (see ff1_palettes.py): value 0 (backdrop) -> transparent, 1/2/3 -> the
monster's three colors.

Usage:
    python3 colorize_monster.py <grayscale.png> <monster name or id> [out.png]
"""
import os
import sys
from PIL import Image
from monster_names import get_names
from ff1_palettes import get_monster_palettes

ROM = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'roms', 'Final Fantasy (USA).nes')

GRAY_LEVELS = [0, 85, 170, 255]  # must match find_ff1_monster_tiles.GRAYSCALE_LEVELS


def resolve_palette(rom, key):
    with open(rom, 'rb') as f:
        data = f.read()
    names = get_names(data)
    palettes = get_monster_palettes(data)
    if key.isdigit():
        mid = int(key)
    else:
        matches = [i for i, n in enumerate(names) if n.lower() == key.lower()]
        if not matches:
            sys.exit(f"monster '{key}' not found")
        mid = matches[0]
    if mid not in palettes:
        sys.exit(f"monster {mid} ({names[mid]}) has no formation/palette")
    return names[mid], palettes[mid][1]


def colorize(gray_img, rgb_palette):
    """Map the 4 grayscale levels to RGBA (level 0 -> transparent)."""
    gray = gray_img.convert('L')
    out = Image.new('RGBA', gray.size)
    lut = {GRAY_LEVELS[i]: (rgb_palette[i] + ((0,) if i == 0 else (255,)))
           for i in range(4)}
    out.putdata([lut.get(p, (0, 0, 0, 0)) for p in gray.getdata()])
    return out


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    src, key = sys.argv[1], sys.argv[2]
    name, palette = resolve_palette(ROM, key)
    out_path = sys.argv[3] if len(sys.argv) > 3 else src.rsplit('.', 1)[0] + '_color.png'
    colorize(Image.open(src), palette).save(out_path)
    print(f"{name}: colorized {src} -> {out_path} with palette {palette}")


if __name__ == "__main__":
    main()
