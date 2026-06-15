"""Aggregate all extracted Final Fantasy (USA) data into one JSON file.

Pulls together monsters (stats + AI + palette), weapons/armor/magic, shops,
prices, treasure, formations, encounter zones, maps (chests/NPCs), and character
classes - reusing the individual extractor modules. The output (ff1_data.json)
backs the browsable HTML atlas (atlas.html).
"""
import json
import os
import struct
import sys

from monster_names import get_names
from print_monsters import create_monster_stats_instance
from item_names import (get_weapon_names, get_armor_names, get_magic_names,
                        get_misc_names, get_gold_names, get_price,
                        decode_bits, ELEMENTS, FAMILIES, TARGETS)
from ff1_palettes import get_monster_palettes
from print_domains import MAP_NAMES
from print_classes import (CLASS_NAMES, starting_stats, starting_mp,
                           exp_to_advance, levelup_summary, STAT_BITS)
from print_magic_permissions import get_magic_permissions
from render_standard_map import find_chests, find_npcs

MON, AI_TABLE, MAGIC_DATA = 0x30530, 0x31030, 0x301f0
WEAPON, ARMOR, FORM, DOMAINS, TREASURE = 0x30010, 0x30150, 0x2c410, 0x2c010, 0x3110
BATTLE_RATES = 0x2cc10  # entry 0 = overworld (unused); standard maps at +1+mid


def hexcol(rgb):
    return '#%02x%02x%02x' % rgb


def monster_ai(data, ai, magic_names):
    if ai == 0xff:
        return None
    e = data[AI_TABLE + ai * 16: AI_TABLE + ai * 16 + 16]
    spells = [magic_names[e[2 + i]] for i in range(8) if e[2 + i] < 64]
    skills = []
    for i in range(4):
        s = e[0xb + i]
        if s != 0xff:
            se = data[MAGIC_DATA + (s + 0x42) * 8: MAGIC_DATA + (s + 0x42) * 8 + 8]
            skills.append({'id': s, 'element': decode_bits(se[2], ELEMENTS)})
    return {'magic_pct': e[0] * 100 // 128, 'spells': spells,
            'skill_pct': e[1] * 100 // 128, 'skills': skills}


def build(data):
    names = get_names(data)
    weapons, armor, magic = get_weapon_names(data), get_armor_names(data), get_magic_names(data)
    palettes = get_monster_palettes(data)
    gold = get_gold_names(data)

    def item_name(iid):
        if 1 <= iid <= len(get_misc_names(data)) and get_misc_names(data)[iid - 1] and iid <= 0x1b:
            return get_misc_names(data)[iid - 1]
        if 0x1c <= iid <= 0x43:
            return weapons[iid - 0x1c]
        if 0x44 <= iid <= 0x6b:
            return armor[iid - 0x44]
        return None

    def treasure_contents(tc):
        b = data[TREASURE + tc]
        nm = item_name(b)
        return nm if nm else f'{get_price(data, b)} G'

    out = {}

    # Monsters
    mons = []
    for mid in range(128):
        s = create_monster_stats_instance(data, MON + mid * 20)
        pid, rgb, _ = palettes.get(mid, (None, [], None))
        mons.append({
            'id': mid, 'name': names[mid], 'hp': s.HP, 'exp': s.exp, 'gold': s.gold,
            'attack': s.strength, 'hits': s.hits, 'hit_pct': s.display_hit,
            'crit': s.crit_rate, 'defense': s.defense, 'evade': s.display_evade,
            'mag_def': s.display_mag_def, 'morale': s.morale,
            'family': decode_bits(s.family_group, FAMILIES),
            'attack_element': decode_bits(s.attack_element, ELEMENTS),
            'weak': decode_bits(s.element_weak, ELEMENTS),
            'resist': decode_bits(s.element_resist, ELEMENTS),
            'ai': monster_ai(data, s.ai, magic),
            'palette': [hexcol(c) for c in rgb],
        })
    out['monsters'] = mons

    # Weapons / armor / magic
    out['weapons'] = []
    for i, nm in enumerate(weapons):
        b = data[WEAPON + i * 8: WEAPON + i * 8 + 8]
        out['weapons'].append({'id': i, 'name': nm, 'damage': b[1], 'hit': b[0],
                               'crit': b[2], 'element': decode_bits(b[4], ELEMENTS),
                               'vs_family': decode_bits(b[5], FAMILIES),
                               'price': get_price(data, 0x1c + i)})
    out['armor'] = []
    for i, nm in enumerate(armor):
        b = data[ARMOR + i * 4: ARMOR + i * 4 + 4]
        out['armor'].append({'id': i, 'name': nm, 'defense': b[1], 'weight': b[0],
                             'resist': decode_bits(b[2], ELEMENTS),
                             'price': get_price(data, 0x44 + i)})
    perms = {p['id']: p for p in get_magic_permissions(data)}
    out['magic'] = []
    for i, nm in enumerate(magic):
        b = data[MAGIC_DATA + i * 8: MAGIC_DATA + i * 8 + 8]
        p = perms.get(i, {})
        out['magic'].append({'id': i, 'name': nm, 'level': p.get('level'),
                             'school': p.get('school'), 'accuracy': b[0], 'effect': b[1],
                             'element': decode_bits(b[2], ELEMENTS),
                             'target': decode_bits(b[3], TARGETS),
                             'classes': p.get('classes', [])})

    # Formations / zones
    forms = []
    TYPES = {0: '9-small', 1: '4-large', 2: 'mixed', 3: 'fiend', 4: 'chaos'}
    for f in range(128):
        e = data[FORM + f * 16: FORM + f * 16 + 16]
        groups = []
        for s in range(4):
            eid = e[2 + s]
            q = e[6 + s]
            if eid < 0x80 and (q & 0x0f) > 0:
                groups.append({'monster': names[eid], 'min': q >> 4, 'max': q & 0x0f})
        forms.append({'id': f, 'type': TYPES.get(e[0] >> 4, str(e[0] >> 4)),
                      'no_run': bool(e[0xd] & 1), 'groups': groups})
    out['formations'] = forms
    out['zones'] = [{'id': d, 'formations': list(data[DOMAINS + d * 8: DOMAINS + d * 8 + 8])}
                    for d in range(128)]

    # Treasure
    out['treasure'] = [{'chest': tc, 'contents': treasure_contents(tc)} for tc in range(256)]

    # Maps (chests + NPCs)
    maps = []
    for mid in range(61):
        chests = [{'x': mx, 'y': my, 'tc': tid, 'contents': treasure_contents(tid)}
                  for mx, my, tid, m in find_chests(data, mid)]
        npcs = [{'id': oid, 'x': mx, 'y': my} for oid, mx, my in find_npcs(data, mid)]
        maps.append({'id': mid, 'name': MAP_NAMES.get(mid, f'map{mid}'),
                     'tileset': data[0x2cd0 + mid], 'encounter_rate': data[BATTLE_RATES + 1 + mid],
                     'chests': chests, 'npcs': npcs})
    out['maps'] = maps

    # Classes
    classes = []
    for c, name in enumerate(CLASS_NAMES):
        counts, strong, mp = levelup_summary(data, c)
        start = starting_stats(data, c)
        start['MP'] = starting_mp(c)
        classes.append({'id': c, 'name': name, 'start': start,
                        'growth': counts, 'strong_hp_levels': strong, 'mp_levels': mp})
    out['classes'] = classes
    out['exp_to_advance'] = [exp_to_advance(data, lv) for lv in range(1, 50)]

    return out


def main():
    rom = sys.argv[1] if len(sys.argv) > 1 else '../roms/Final Fantasy (USA).nes'
    out_path = sys.argv[2] if len(sys.argv) > 2 else '../output/ff1_data.json'
    with open(rom, 'rb') as f:
        data = f.read()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    result = build(data)
    with open(out_path, 'w') as f:
        json.dump(result, f, separators=(',', ':'))
    counts = {k: len(v) for k, v in result.items() if isinstance(v, list)}
    print(f"wrote {out_path} ({os.path.getsize(out_path)} bytes): {counts}")


if __name__ == "__main__":
    main()
