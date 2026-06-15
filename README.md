# Final Fantasy (NES) - ROM Analysis Project

## Overview
Reverse engineering project for extracting monster data, graphics, and game content from the NES Final Fantasy (USA) ROM using Python scripts and Ghidra analysis.

## Platform Information
- **Console**: Nintendo Entertainment System (NES)
- **Game**: Final Fantasy (USA)
- **ROM File**: `Final Fantasy (USA).nes`
- **Mapper**: MMC1 (Mapper 1)
- **CHR**: Uses CHR RAM (no CHR ROM)
- **Analysis Tools**: FCEUX debugger, ImHex, Python, Ghidra

## Project Structure

```
finalfantasy/
├── finalfantasy.gpr          # Ghidra project file
├── finalfantasy.rep/         # Ghidra analysis repository
├── docs/                     # Documentation and notes
│   ├── README.md            # Original monster extraction notes
│   ├── CLAUDE.md            # Original project guide
│   └── .gitignore
├── roms/                     # ROM files and debug data
│   ├── Final Fantasy (USA).nes
│   ├── Final Fantasy (USA).cdl  # Code/Data Log
│   ├── Final Fantasy (USA).fdb  # FCEUX debug symbols
│   └── Jeopardy! (U).nes    # Additional NES ROM for testing
├── atlas.html                # Browsable data atlas (loads output/ff1_data.json)
├── scripts/                  # Python analysis scripts (see CLAUDE.md for all)
│   ├── monster_names.py / print_monsters.py / print_ai.py   # monsters + AI
│   ├── extract_monster_sprites.py / print_palettes.py       # color sprites
│   ├── print_weapons.py / print_armor.py / print_magic.py   # equipment + spells
│   ├── print_prices.py / print_shops.py / print_treasure.py # economy
│   ├── print_formations.py / print_domains.py               # encounters + zones
│   ├── print_classes.py / extract_class_sprites.py          # class data + sprites
│   ├── render_standard_map.py / render_overworld.py         # map renderers
│   ├── render_formations.py                                 # battle-scene renderer
│   ├── export_json.py                                       # JSON for the atlas
│   ├── item_names.py / ff1_palettes.py / load_tbl.py        # shared helpers
│   └── find_strings.py / print_dialog.py / nes_color_converter.py / ...
├── output/                   # Generated PNGs + ff1_data.json (gitignored)
├── tools/                    # Data files and tables
│   ├── final_fantasy.tbl    # FF1 character encoding table
│   ├── strings.txt          # Extracted strings
│   ├── jeopardy*.tbl        # Jeopardy encoding tables
│   └── jeopardy.txt         # Jeopardy extracted text
└── images/                   # Reference screenshots
    ├── ppu.png              # PPU viewer (character tiles at $80)
    ├── name_table.png       # Name table viewer (IMP battle)
    └── intro.png            # Intro screen
```

## Key Findings

### Monster Data Structure
Monster stats are stored as 128 sequential structs (20 bytes each) starting at ROM offset **0x30530**:

All 20 bytes are now identified (see `scripts/print_monsters.py`):

```c
struct MonsterStats {
    u16 exp;            // Experience points
    u16 gold;           // Gold dropped
    u16 HP;             // Hit points
    u8 morale;          // Morale (run level = (morale-80)/2)
    u8 ai;              // AI script index (0xff = none); see print_ai.py
    u8 agility;         // Evade (displayed as agility/2)
    u8 defense;         // Damage absorbed
    u8 hits;            // Number of attacks
    u8 hit_rate;        // Displayed hit% = 84 + hit_rate/2
    u8 strength;        // Damage per hit
    u8 crit_rate;       // Critical hit %
    u8 attack_element;  // Element of the monster's attack (set when it inflicts a status)
    u8 ailment;         // Attack-inflicted status ailment
    u8 family;          // Monster family bitvector
    u8 mag_def;         // Magic defense (displayed as mag_def/2)
    u8 weak;            // Elemental weakness bitvector
    u8 resist;          // Elemental resistance bitvector
};
```

Field meanings come from the FF1 disassembly (Entroper/FF1Disassembly,
`some formats.txt`) plus cross-referencing the gamercorner monster guide.

### Key ROM Offsets
- **Monster names**: 0x2d5f0–0x2d951 · **Monster stats**: 0x30530 (128 × 20)
- **Monster AI**: 0x31030 · **Enemy sprites (CHR)**: 0x1c010+ / 0x20010+
- **Weapons**: 0x30010 (40 × 8) · **Armor**: 0x30150 (40 × 4) · **Magic**: 0x301f0 (64 × 8)
- **Prices**: 0x37c10 · **Treasure** (lut_Treasure): 0x3110 · **Shops**: 0x38310
- **Formations**: 0x2c410 (128 × 16) · **Battle domains**: 0x2c010 (128 × 8)
- **Battle palettes**: 0x30f30 · **Class starting stats**: 0x3050 · **Level-up**: 0x2d0a4
- **Overworld map**: rows via lut_OWPtrTbl 0x4010 · **Standard maps**: lut_SMPtrTbl 0x10010

(See `CLAUDE.md` for the full offset/format reference.)

### Character Encoding
Custom character encoding map (0x80-0xC5) for FF1's text system:
- Located in `tools/final_fantasy.tbl`
- Used by string extraction scripts

### Element & Family Bitvectors

**Element** (weak/resist/attack-element, shared with weapons & magic):
```
0x01 Status  0x02 Poison  0x04 Time  0x08 Death
0x10 Fire    0x20 Ice     0x40 Lightning  0x80 Earth
```
Verified: STOP=Time, RUB=Death, QAKE=Earth, FIRE/ICE/LIT match.

**Family** (monster category, also the weapon "vs family" bonus):
```
0x02 Dragon  0x04 Giant  0x08 Undead  0x10 Were
0x20 Aquatic 0x40 Mage   0x80 Regen
```

## Using the Scripts

### Prerequisites
- Python 3.x
- ROM file: `roms/Final Fantasy (USA).nes`

### Extract Monster Names
```bash
cd scripts/
python3 monster_names.py ../roms/Final\ Fantasy\ \(USA\).nes
```

### Extract Complete Monster Data
```bash
python3 print_monsters.py ../roms/Final\ Fantasy\ \(USA\).nes
```

### Find All Strings in ROM
```bash
python3 find_strings.py ../roms/Final\ Fantasy\ \(USA\).nes
```

### Extract Monster Sprites (full color)
```bash
python3 extract_monster_sprites.py        # 123 sprites -> output/monsters/
```

### Render Maps
```bash
python3 render_standard_map.py            # 61 towns/dungeons (plain + annotated)
python3 render_overworld.py               # overworld (plain + annotated)
```

### Build & Browse the Data Atlas
```bash
python3 export_json.py                     # -> output/ff1_data.json
cd .. && python3 -m http.server            # then open http://localhost:8000/atlas.html
```

## Analysis Tools Used

### FCEUX
NES emulator with powerful debugging features:
- **PPU Viewer** - View character tiles and sprites in VRAM
- **Name Table Viewer** - View current screen layout
- **Debugger** - 6502 disassembly and memory inspection
- **Code/Data Logger** - Generate .cdl files for tracking code execution

### ImHex
Hex editor with pattern language for structured data:
- Custom pattern file for MonsterStats struct
- Applied pattern at 0x30530 to view all 128 monsters
- Bitvector visualization for elements and families

### Python Scripts
Custom scripts for automated extraction and analysis:
- Character encoding with custom table files
- Struct unpacking for binary data
- String extraction with filtering

## Current Status

### Completed ✅
- Monster names extracted (all 128 monsters)
- Monster stats fully decoded (all 20 struct bytes identified)
- Character encoding table rebuilt from DataCrystal (NA section, with DTE pairs)
- String extraction working (intro text at 0x37f2f and dialog at ~0x28000 extract cleanly)
- Dialog dumper (print_dialog.py walks the 256-entry pointer table)
- Monster sprite sheets extracted (grayscale, via find_ff1_monster_tiles.py)
- Weapon / armor / magic data tables extracted and verified (print_weapons/armor/magic.py)
- Shop inventories extracted (print_shops.py)
- Item prices extracted and verified (print_prices.py)
- Treasure chest contents extracted (print_treasure.py; item chests verified)
- Enemy formations extracted and verified (print_formations.py)
- Encounter zones / battle domains extracted and verified (print_domains.py)
- Location->zone mapping decoded (overworld 8x8 grid + map_id+0x40, from bank_0F.asm)
- Standard-map zones labeled by place name (print_domains.py MAP_NAMES)
- Monster stats show guide-style display values (Hit% = 84+raw/2, Eva/MagDef =
  raw/2, RunLv = (morale-80)/2); byte E pinned as attack element
- Enemy AI scripts extracted - spells & skills each monster uses (print_ai.py)
- Monster battle palettes mapped (print_palettes.py)
- All 123 monster sprites extracted in full color including fiends/Chaos,
  black background like the game (extract_monster_sprites.py)
- Element & family bitfields fully decoded
- Overworld map rendered in color with entrance + encounter-zone overlays (render_overworld.py)
- All 61 standard maps rendered in color, plus annotated versions with chest
  and NPC sprites overlaid (render_standard_map.py)
- Character classes: starting stats, EXP table, level-up growth (print_classes.py)
- Class sprites extracted pixel-exact (extract_class_sprites.py): overworld
  'mapman' (correct per-class palette split top/bottom row) + battle sprite
  (standing pose, class battle palette). Verified: black mage blue robe/yellow
  hat, white mage white robe/red trim
- Enemy formations rendered as battle scenes (render_formations.py): all monsters
  placed at their real on-screen slots (9-small grid, 4-large, mix, fiend/Chaos)
- Verified vs external guides: monsters (gamercorner), treasure & dungeons
  (mikesrpgcenter), weapons/armor stats & prices

### Data atlas (JSON + HTML)
- `scripts/export_json.py` -> `output/ff1_data.json` aggregates everything
- `atlas.html` browses it (monsters, items, magic, treasure, formations as
  battle scenes, zones, maps with chest/NPC overlays, classes with overworld +
  battle sprites). Sprite-on-hover throughout. Usage:
  `python3 scripts/export_json.py && python3 -m http.server` then open atlas.html

### In Progress / minor 🔄
- Shop town/type labels and clinic/caravan price slots
- Weapon/armor category words (second word from icon tile)
- Per-NPC sprite palette is per-map (game uses one scheme); not per-object

### TODO ⏸️
- Magic-learning table (which class learns which spell at which level)
- Extract music and sound effects
- Overworld object overlay (NPCs/bridge/canal)

## Reference Materials

### ROM/RAM Maps
- [Final Fantasy ROM Map](https://datacrystal.tcrf.net/wiki/Final_Fantasy/ROM_map)
- [Final Fantasy RAM Map](https://datacrystal.tcrf.net/wiki/Final_Fantasy/RAM_map)
- [Game Corner Monster Guide](https://guides.gamercorner.net/ff/monsters/) (stat verification)
- [Entroper/FF1Disassembly](https://github.com/Entroper/FF1Disassembly) (offsets & formats)
- [Mike's RPG Center - FF1](https://mikesrpgcenter.com/ffantasy/) (treasure/equipment verification)

### NES Development
- [6502 Instruction Reference](https://www.nesdev.org/obelisk-6502-guide/reference.html)
- [NES Cart Database](https://nescartdb.com/profile/view/715/final-fantasy)
- [Writing NES Disassembler](https://medium.com/hard-mode/nes-emulator-writing-a-disassembler-and-memory-viewer-4727e76de57)

## Example Monster Data

```
NAME      HP   GOLD  EXP   ATK  HITS FAMILY   WEAK  RESIST
IGUANA    92   50    153   18   1    Dragon   -     -
GIANT     240  879   879   38   1    Giant    -     -
FrGIANT   336  1752  1752  60   1    Giant    Fire  Ice
R.GIANT   300  1506  1506  73   1    Giant    Ice   Fire
SAHAG     28   30    30    10   1    Aquatic  Lit   Fire|Earth
```

(Full data for all 128 monsters — with AI, palettes, and the rest — is in the
JSON export / atlas.)

## Notes

- Most data was decoded with the Entroper/FF1Disassembly as a reference for
  offsets and formats, then verified against the ROM and external guides.
- Character names use FF1's custom encoding plus DTE pairs for dialog text.
- Lesson learned: the treasure table was briefly read from 0x3f110 (the RNG
  table) instead of 0x3110 (lut_Treasure) — caught by cross-referencing the
  mikesrpgcenter dungeon maps. Cross-checking offsets against guides pays off.

## License & Usage
This is a reverse engineering project for educational and preservation purposes. All game content is property of Square Enix.
