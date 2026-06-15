"""Build a connectivity graph of the whole game world and emit a Graphviz DOT
file (plus a rendered SVG if `dot` is installed).

Nodes:
  * Overworld (single hub)
  * 61 standard maps, typed town / castle / dungeon
  * Shops (weapon/armor/magic/clinic/inn/item/caravan), attached to their town

Edges:
  * Overworld -> map     : overworld entrance tiles (lut_EntrTele_Map)
  * map -> map           : normal teleports / stairs (teleport_links)
  * map -> Overworld     : exit teleports
  * town -> shop         : shop-entrance door tiles (property byte1 = shop id)

Data all comes from the ROM (no Ghidra): overworld entrances + map teleports as
in render_overworld / render_standard_map; shop ids from town door tiles
(byte1), shop type from lut_ShopTypes (file 0x3ebc5).

Outputs:
  output/ff1_map_graph.dot   - the DOT graph
  output/map_graph.svg       - rendered with clickable map nodes (if dot present)
"""
import os
import struct
import subprocess
import sys

from print_domains import MAP_NAMES
from render_standard_map import teleport_links, decompress, PROP, TILESETS, SMPTR
from render_overworld import decompress_grid, OWPROP, ENTR_MAP

SHOP_TYPES_LUT = 0x3ebc5
SHOP_TYPE = ['Weapon', 'Armor', 'White Magic', 'Black Magic', 'Clinic', 'Inn', 'Item', 'Caravan']
SHOP_COLOR = {'Weapon': '#d98c8c', 'Armor': '#8ca6d9', 'White Magic': '#eeeeee',
              'Black Magic': '#c39bd3', 'Clinic': '#f5b7c4', 'Inn': '#9bd3a0',
              'Item': '#e8c07d', 'Caravan': '#c8a27a'}


def map_type(mid, name):
    if mid <= 7:
        return 'town'
    if 'Castle' in name:
        return 'castle'
    return 'dungeon'


def overworld_entrances(data):
    """Distinct destination maps reachable from overworld entrance tiles."""
    grid = decompress_grid(data)
    dests = set()
    for row in grid:
        for m in row:
            p = data[OWPROP + m * 2 + 1]
            if p & 0x80:
                dests.add(data[ENTR_MAP + (p & 0x7f)])
    return dests


def town_shops(data, mid):
    """Shop ids reachable from door tiles in a town map (door prop byte1 = id)."""
    ts = data[TILESETS + mid]
    pb = PROP + ts * 256
    grid = decompress(data, SMPTR + struct.unpack_from('<H', data, SMPTR + mid * 2)[0])
    ids = set()
    for m in set(grid):
        b0, b1 = data[pb + m * 2], data[pb + m * 2 + 1]
        if b1 and (b0 & 0xc0) == 0 and (b0 & 0x1e) in (0x02, 0x04, 0x06):
            ids.add(b1)
    return sorted(ids)


def shop_type(data, sid):
    t = data[SHOP_TYPES_LUT + sid]
    return SHOP_TYPE[t] if t < len(SHOP_TYPE) else f'shop{t}'


def build_dot(data):
    L = ['digraph FF1 {',
         '  graph [bgcolor="#14161c", rankdir=LR, fontname="sans-serif", nodesep=0.25, ranksep=1.1];',
         '  node  [style="filled,rounded", fontname="sans-serif", fontsize=11, color="#000000"];',
         '  edge  [color="#5599cc", penwidth=1.2];',
         '  ow [label="OVERWORLD", shape=doublecircle, fillcolor="#f8c838", '
         'fontsize=15, URL="#m_ow"];']

    style = {'town': ('house', '#fff3c4'), 'castle': ('box', '#a9c7e8'),
             'dungeon': ('ellipse', '#cfd4dd')}
    for mid in range(61):
        name = MAP_NAMES.get(mid, f'map{mid}')
        shape, fill = style[map_type(mid, name)]
        L.append(f'  m{mid} [label="{name}", shape={shape}, fillcolor="{fill}", URL="#m{mid}"];')

    # overworld entrances
    for dm in sorted(overworld_entrances(data)):
        L.append(f'  ow -> m{dm} [color="#cc4444", penwidth=1.6];')

    # map -> map teleports and map -> overworld exits
    for mid in range(61):
        lk = teleport_links(data, mid)
        for m in lk['maps']:
            if m['dest'] != mid:
                L.append(f'  m{mid} -> m{m["dest"]};')
        if lk['exits']:
            L.append(f'  m{mid} -> ow [color="#55aa55", style=dashed];')

    # shops attached to towns
    for mid in range(8):
        for sid in town_shops(data, mid):
            typ = shop_type(data, sid)
            L.append(f'  s{sid} [label="{typ}", shape=note, fontsize=9, '
                     f'fillcolor="{SHOP_COLOR.get(typ, "#ccc")}", '
                     f'tooltip="{MAP_NAMES.get(mid)} {typ} (shop #{sid})"];')
            L.append(f'  m{mid} -> s{sid} [color="#888888", style=dotted, arrowhead=none];')

    L.append('}')
    return '\n'.join(L)


def main():
    rom = sys.argv[1] if len(sys.argv) > 1 else '../roms/Final Fantasy (USA).nes'
    out_dir = sys.argv[2] if len(sys.argv) > 2 else '../output'
    with open(rom, 'rb') as f:
        data = f.read()
    os.makedirs(out_dir, exist_ok=True)
    dot = build_dot(data)
    dot_path = os.path.join(out_dir, 'ff1_map_graph.dot')
    with open(dot_path, 'w') as f:
        f.write(dot)
    print(f"wrote {dot_path}")

    svg_path = os.path.join(out_dir, 'map_graph.svg')
    try:
        subprocess.run(['dot', '-Tsvg', dot_path, '-o', svg_path], check=True)
        print(f"rendered {svg_path}")
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print(f"(graphviz 'dot' not available - DOT file written, SVG skipped: {e})")


if __name__ == '__main__':
    main()
