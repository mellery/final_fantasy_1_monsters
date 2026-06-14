"""Print each monster's battle palette (which colors its sprite uses).

See ff1_palettes.py for how the monster -> palette mapping is derived.
"""
import sys
from monster_names import get_names
from ff1_palettes import get_monster_palettes


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

    for mid in range(128):
        if mid not in palettes:
            continue
        pid, rgb, raw = palettes[mid]
        swatches = ' '.join(f"#{r:02x}{g:02x}{b:02x}" for r, g, b in rgb)
        print(f"{names[mid]:9s} pal{pid:2d}: {swatches}")


if __name__ == "__main__":
    main()
