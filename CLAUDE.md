# Final Fantasy (NES) - Project Guide for Claude Code

## Overview
This is a ROM analysis project for extracting and documenting monster data, graphics, and game content from the NES Final Fantasy (USA) ROM. The project combines Python-based data extraction with Ghidra binary analysis.

## Project Organization

This project was reorganized from `/home/mike/src/final_fantasy_1_monsters` and merged into the Ghidra projects structure for better organization.

### Directory Structure
- **docs/** - Original documentation and research notes
- **roms/** - NES ROM files and FCEUX debug data (.cdl, .fdb)
- **scripts/** - Python scripts for data extraction and analysis
- **tools/** - Character encoding tables (.tbl) and extracted data
- **images/** - Reference screenshots from FCEUX debugger
- **finalfantasy.gpr** - Ghidra project (for future disassembly work)
- **finalfantasy.rep/** - Ghidra analysis repository

## Key Files and Scripts

### Monster Data Extraction (Core Scripts)

#### `scripts/monster_names.py` ⭐
**Purpose**: Extract all 128 monster names from ROM

**Usage**:
```bash
python3 monster_names.py ../roms/Final\ Fantasy\ \(USA\).nes
```

**How it works**:
- Reads ROM at offset **0x2d5f0** (monster names region)
- Uses custom character encoding table (0x80-0xC5)
- Outputs numbered list of all monster names

**Key Details**:
- Monster names stored as variable-length strings
- Uses FF1-specific character encoding (not ASCII)
- Provides `get_names()` function for import by other scripts

#### `scripts/print_monsters.py` ⭐
**Purpose**: Extract complete monster data (names + stats)

**Usage**:
```bash
python3 print_monsters.py ../roms/Final\ Fantasy\ \(USA\).nes
```

**How it works**:
- Imports `get_names()` from `monster_names.py`
- Reads 128 monster structs from ROM offset **0x30530**
- Unpacks binary data using struct format: `'HHHBBBBBBBBBBBBBB'`
- Outputs formatted table with all monster statistics

**Key Data Structure** (all 20 bytes identified - see scripts/print_monsters.py):
```python
@dataclass
class MonsterStats:
    exp: int           # uint16
    gold: int          # uint16
    HP: int            # uint16
    morale: int        # uint8 - run level = (morale-80)//2
    ai: int            # uint8 - AI script index (0xff=none); see print_ai.py
    agility: int       # uint8 - evade; displayed as agility//2
    defense: int       # uint8 - damage absorbed
    hits: int          # uint8 - number of attacks
    hit_rate: int      # uint8 - displayed hit% = 84 + hit_rate//2
    strength: int      # uint8 - damage per hit
    crit_rate: int     # uint8
    attack_element: int# uint8 - element of the monster's attack (ELEMENTS bitfield);
                       #         set only when its attack inflicts a status ailment
    ailment: int       # uint8 - attack-inflicted status ailment
    family: int        # uint8 - family bitvector
    mag_def: int       # uint8 - displayed as mag_def//2
    weak: int          # uint8 - element bitvector
    resist: int        # uint8 - element bitvector
```
Field meanings from the FF1 disassembly (some formats.txt) plus the gamercorner
guide (guides.gamercorner.net/ff/monsters/), which confirmed the display formulas
and let byte E be pinned as the attack element (non-zero iff a status attack).

### String and Graphics Extraction

#### `scripts/find_strings.py`
**Purpose**: General-purpose string extractor for NES ROMs

**How it works**:
- Scans ROM for sequences of valid FF1 characters (0x80-0xC5)
- Outputs all strings > 2 characters with hex offsets
- Used to locate monster names initially

#### `scripts/find_ff1_monster_tiles.py` ⭐
**Purpose**: Extract monster sprite sheets (grayscale) from the ROM's tile data

**Usage** (run from an output directory; writes `tiles_<offset>.png` sprite sheets to cwd):
```bash
cd output/sprites/
python3 ../../scripts/find_ff1_monster_tiles.py "../../roms/Final Fantasy (USA).nes"
```

**How it works**:
- Reads 16-byte NES tiles (2 bitplanes) starting at ROM offset 0x1c020
- Renders tiles as grayscale (2-bit pixel values mapped to 0/85/170/255)
- Stitches tiles into per-monster sprite sheets, including hand-mapped blank-tile
  layouts for the large bosses (Lich, Kary, Kraken, Tiamat, Chaos)

**Note**: Color palette support was removed — the palette code never worked
correctly and grayscale output is sufficient.

#### `scripts/find_tiles.py` & `scripts/find_pallets.py`
**Purpose**: General NES tile and palette extraction

**Note**: Generic NES graphics utilities, not FF1-specific

### Utility Scripts

#### `scripts/load_tbl.py`
**Purpose**: Load and parse character encoding table files

**Used by**: All string extraction scripts
**Tables**: `tools/final_fantasy.tbl`, `tools/jeopardy*.tbl`

#### `scripts/nes_color_converter.py`
**Purpose**: Convert NES palette values to RGB

#### `scripts/create_image_grid.py`
**Purpose**: Create image grids from extracted tiles

### Item / Equipment / Magic / Shop Extraction

#### `scripts/print_weapons.py` / `print_armor.py` / `print_magic.py` ⭐
**Purpose**: Decode the fixed-size weapon (40x8), armor (40x4), and magic (64x8)
record tables into readable tables with names, stats, and decoded element/
family/target bitfields. Offsets and fields verified against known FF1 values.

#### `scripts/print_shops.py` ⭐
**Purpose**: Decode shop inventories via the pointer table at 0x38310. Maps the
unified item-id namespace to names and infers shop type from contents.
**Limitations**: Weapon/armor names are first-words only (the category word
comes from an icon tile, not decoded), so duplicates like "Silver, Silver"
appear. Clinic/caravan price slots and town/shop-type grouping are not decoded.

#### `scripts/print_prices.py` ⭐
**Purpose**: Decode the per-item buy-price table at 0x37c10. Magic is priced by
spell level. Verified by the 'Power' item's 12345 placeholder and consumable prices.

#### `scripts/print_treasure.py` ⭐
**Purpose**: Decode the 256-chest contents table at 0x3110 (lut_Treasure). Item chests
(weapons/armor/quest/consumables) decode to verified names; gold chests are
flagged by id. Use `--items` to list only item chests.

#### `scripts/print_formations.py` ⭐
**Purpose**: Decode the 128 enemy formations (encounter battle groups) at
0x2c400 - which monsters appear together, quantities, type, surprise, no-run.
Verified against known FF1 encounters (3-5 IMP first battle, the Fiends, Chaos).

#### `scripts/print_palettes.py` / `colorize_monster.py` ⭐
**Purpose**: View monster sprites in color. Battle palettes are at 0x30f30
(64 x 4 NES colors); a monster's palette comes from the first formation that
uses it (formation byte D selects palette A/B per slot - see ff1_palettes.py).
`print_palettes.py` lists each monster's colors; `colorize_monster.py` recolors
a grayscale sprite PNG (from find_ff1_monster_tiles.py) using that palette.
Verified: Chaos renders gold/purple, Kraken purple tentacles, FrWOLF icy blue.

#### `scripts/extract_monster_sprites.py` ⭐
**Purpose**: Extract all 123 monster sprites in full color (black background,
like the game). Regular monsters map to a sprite slot: CHR page = formation
byte0 low nibble; gfx = (byte1 >> 2*slot) & 3, where bit0 = size (0=small 4x4,
1=medium 6x6) and bit1 = image. Page -> ROM: 0-7 at 0x1c000+page*0x800, 8+ at
0x20000+(page-8)*0x800; offsets within page: gfx0 +0x130, gfx2 +0x230 (small),
gfx1 +0x330, gfx3 +0x570 (medium). The fiends/Chaos (ids 119-127) use a TSA
grid layout (BOSS_SPRITES). Colored via each monster's battle palette. Writes
to output/monsters/ as NNN_NAME.png. Verified visually across all pages.

#### `scripts/print_sprite_groups.py`
**Purpose**: Report each monster's sprite CHR page and palette (the grouping
underlying extract_monster_sprites.py).

#### `scripts/print_ai.py` ⭐
**Purpose**: Decode enemy AI scripts (lut_EnemyAi at 0x31030, 16 bytes each) -
which spells (8 slots) and special skills (4 slots) each monster casts, and the
rates. Monster stat byte 7 = AI index. Skills index the extended magic table at
(skill+0x42). Verified: Tiamat breathes all 4 elements, Kary casts FIR2/FIR3.

#### `scripts/print_domains.py` ⭐
**Purpose**: Decode the 128 encounter zones (battle domains) at 0x2c000 - the
"where enemies appear" table. Each zone lists its 8 possible formations expanded
to monster names. Verified: zone 1 = endgame (WarMECH), zones 29-30 = start area.

#### `scripts/item_names.py`
**Purpose**: Shared helpers - weapon/armor/magic/consumable name extraction,
the unified item-id map, prices, gold-name strings, and element/family/target
bitfield decoding. Imported by the print_* scripts above.

### Map Rendering

#### `scripts/render_standard_map.py` ⭐
**Purpose**: Render all 61 standard maps (towns/castles/dungeons) to PNG, both
plain (NN_Name.png) and annotated (NN_Name_annotated.png). `--list` dumps
chests/NPCs as text. Map pipeline: map->tileset (lut_Tilesets, 0x2cd0+map);
RLE-decompress (lut_SMPtrTbl 0x10010, entry is an offset so data=0x10010+ptr);
metatile->4 CHR tiles (TSA 512B/tileset at 0x1010+ts*512) + palette (tsa_attr
0x410+ts*128); tileset CHR 0xc010+ts*0x800 (bank 03); map palette 0x2010+map*0x30.
64x64 metatiles -> 1024px. Overlay: chests from tile props (prop ssss==4, TC id
in 2nd byte; contents from lut_Treasure 0x3110, gold amount = get_price(id));
NPCs drawn as their actual sprite (lut_MapObjGfx 0x2e10[obj]->graphic, CHR at
lut_MapObjCHR 0xa210+gfx*0x100, tiles 0,1,4,5, sprite palette 0).

#### `scripts/render_overworld.py` ⭐
**Purpose**: Render the 256x256 overworld to PNG (4096x4096 + preview). Rows
RLE-compressed, pointer table lut_OWPtrTbl at 0x4010 (bank 01). OW tileset is one
0x400 block at file 0x10: prop(+0), TSA ul/ur/dl/dr(+0x100/180/200/280),
attr(+0x300), palette(+0x380, 4x4 NES colors). OW BG CHR bank 02 (file 0x8010).

### Map / RLE format
- RLE: 0x00-0x7f = one metatile; 0x80-0xfe = run (tile=b&0x7f, next byte=count,
  0->256); 0xff = terminator. See DecompressMap in bank_0F.asm.

## Important ROM Offsets

### Monster Data
- **Monster Names Start**: 0x2d5f0
- **Monster Names End**: 0x2d951
- **Monster Stats Start**: 0x30530
- **Monster Stats Size**: 20 bytes per monster
- **Total Monsters**: 128

### Item / Equipment / Magic Data (all verified against known FF1 values)
- **Weapon Data**: 0x30010, 40 entries x 8 bytes
  (hit%, damage, crit%, spell-on-use, element, family-bonus, sprite, palette)
- **Armor Data**: 0x30150, 40 entries x 4 bytes (weight, defense, element-resist, b3)
- **Magic Data**: 0x301f0, 64 entries x 8 bytes
  (accuracy, effectivity, element, target, routine, gfx, palette, unused)
- **Magic Names**: 0x2be13, 64 x 5 bytes (clean fixed-width)
- **Weapon+Armor Names**: 0x2b9cc, packed 0x00-delimited stream (0-39 weapons, 40-79 armor)
- **Quest/Consumable Names**: 0x2b910, 0x00-delimited (IDs 0x01-0x1b; 0x12-0x15 unused)
- **Shop Pointer Table**: 0x38310, little-endian CPU pointers ($8000 bank, file = ptr + 0x30000);
  each points to a 0x00-terminated item-id list. Unused slots point back into the table.

### Unified item-id namespace (shops, treasure)
- 0x01-0x11 quest items, 0x16-0x1b consumables, 0x1c-0x43 weapons,
  0x44-0x6b armor, 0xb0-0xef magic
- In treasure context, 0x6c-0xff are gold chests instead of magic

### Prices
- **Price Table**: 0x37c10, indexed by item id, 2 bytes LE (ids 0x01-0xef).
  Quest items = 0 (unsellable). Magic priced by level: 100/400/1500/4000/
  8000/20000/45000/60000 for levels 1-8.

### Treasure
- **Chest Contents**: 0x3110 (lut_Treasure, $B100 bank 0), flat array of 256 item ids (one byte per chest).
  Item ids 0x01-0x6b decode to verified names; ids 0x6c-0xff are gold chests
  whose exact amount is not yet decoded.

### Encounters
- **Formation Table**: 0x2c400, 128 entries x 16 bytes. Format (from the
  Entroper/FF1Disassembly "some formats.txt"): byte0 hi nibble = type
  (0=9small,1=4large,2=mixed,3=fiend,4=chaos); bytes 2-5 = enemy ids;
  bytes 6-9 = quantity (hi nibble min, lo nibble max); byteC = surprise rate;
  byteD bit0 = no-run; bytes E-F = "formation B" alt quantities for slots 0-1.
  Verified: formation 1 = 3-5 IMP, 116-119 = the four Fiends, 124 = CHAOS.
- **Battle Domains (encounter zones)**: 0x2c000, 128 zones x 8 bytes. Each byte
  is a formation ref; bit 7 selects the formation's B variant, low 7 bits are
  the formation index. The overworld grid and dungeon maps reference a domain.
  Verified: zone 1 = endgame (WarMECH), zones 29-30 = Coneria start (IMP/etc).
- **Map encounter rates**: 0x2cc00, 64 bytes (one rate per map; separate).
- Offsets confirmed by Entroper/FF1Disassembly bin names (0B_8000_battledomains,
  0B_8400_battleformations, 0B_8C00_mapencounterrates). Note the iNES 16-byte
  header: file = 0x10 + bank*0x4000 + (CPU-0x8000), so bank 0B $8000 = file 0x2c010.
- **Location -> zone mapping** (computed in bank_0F.asm, not a table):
  - Overworld land: domain = (playerY>>5)*8 + (playerX>>5) -> 0-63 (8x8 grid,
    each cell = 32x32 overworld tiles)
  - Overworld river: domain 0x40 (upper map half) / 0x41 (lower half)
  - Overworld sea: domain 0x42
  - Standard maps (towns/dungeons): domain = map_id + 0x40 -> 64-127
  Verified: sea domain 0x42 = SAHAG/SHARK/pirates, river = HYDRA/GATOR, OW grid
  cells 18/20/24 = imps (Coneria), Earth Cave B1 (map 13) = COBRA/OGRE/MUMMY,
  Sky Palace 5F (map 51, domain 115) = WarMECH, ToFR Earth (map 55) = golems/EARTH.
- Standard map id -> name from the FF1Randomizer MapId enum (built on this same
  disassembly); 0-7 towns, 8-60 castles/dungeon floors, 61-63 unused. Labeled in
  print_domains.py (MAP_NAMES).
- GetBattleFormation weights the 8 formations per domain via a 64-byte RNG-index
  table (lut_FormationWeight in bank 0F), so they are not equally likely.

### Element bitfield (weapons, magic, monster weak/resist)
- 0x01 Status, 0x02 Poison, 0x04 Time, 0x08 Death,
  0x10 Fire, 0x20 Ice, 0x40 Lightning, 0x80 Earth
  (verified: STOP=Time, RUB=Death, QAKE=Earth, FIRE/ICE/LIT match)

### PPU/Graphics
- **Character Tiles**: PPU $80 (verified in FCEUX PPU Viewer)
- **CHR Type**: CHR RAM (not ROM-based)

## Character Encoding

FF1 uses custom character encoding starting at 0x80:
- **Encoding Range**: 0x80 to 0xC5 (plus DTE pairs 0x1A-0x6F for dialog text)
- **Table File**: `tools/final_fantasy.tbl`
- **Source**: https://datacrystal.tcrf.net/wiki/Final_Fantasy/TBL (North American section)
- **Format**: Standard .tbl format (hex=character mappings); 0x00 is the string
  terminator and is intentionally unmapped; DTE entries have significant trailing spaces

All string extraction scripts depend on this encoding table.

## Bitvector Decoding

### Element Bitvectors (weak/resist fields)
```
0x01 = Unknown
0x02 = Unknown
0x04 = Unknown
0x08 = Unknown
0x10 = Fire
0x20 = Cold
0x40 = Lightning
0x80 = Earth
```

### Family Bitvectors
```
0x02 = Dragon
0x04 = Giant
0x20 = Aquatic
0x40 = Spellcaster
```

**Note**: Multiple bits can be set (e.g., 0x22 = Aquatic + Dragon)

## Tools and Analysis Methods

### FCEUX Debugger
Primary tool for initial ROM analysis:
- **PPU Viewer**: Identified character tiles at $80
- **Name Table Viewer**: Verified monster names (IMP = 92 96 99)
- **Memory Viewer**: Located data structures
- **Code/Data Logger**: Generated .cdl file for code coverage

**Why FCEUX over Ghidra**:
- Better NES-specific debugging features
- Real-time memory inspection during gameplay
- PPU/graphics visualization
- Immediate feedback for hypothesis testing

### ImHex Pattern Language
Used for structured data visualization:
- Created custom pattern for MonsterStats struct
- Applied pattern array at 0x30530
- Visualized all 128 monsters simultaneously
- Experimented with bitvector enums

**Example Pattern** (from docs/README.md):
```c
struct MonsterStats {
    u16 exp;
    u16 gold;
    u16 HP;
    // ... (see README.md for full pattern)
};

MonsterStats Monster[128] @ 0x30530;
```

### Python Scripts
Automated extraction and validation:
- Struct unpacking with Python's `struct` module
- Custom character encoding with dictionary mappings
- File I/O for ROM reading
- Modular design (monster_names.py imported by print_monsters.py)

## Working with This Project

### Running Scripts
All scripts default to `Final Fantasy (USA).nes` if no ROM specified:
```bash
cd scripts/
python3 print_monsters.py  # Uses default ROM path
python3 monster_names.py ../roms/custom.nes  # Custom ROM
```

### Understanding the Data Flow
1. **Character Encoding**: `load_tbl.py` loads `tools/final_fantasy.tbl`
2. **Name Extraction**: `monster_names.py` reads 0x2d5f0, decodes with encoding
3. **Stats Extraction**: `print_monsters.py` reads 0x30530, unpacks binary structs
4. **Merged Output**: Names + stats combined for complete monster data

### Extending the Analysis

**To add new field decoding**:
1. Update `MonsterStats` dataclass in `print_monsters.py`
2. Document findings in README.md with cross-references
3. Update bitvector decoding sections with new discoveries

**To extract graphics**:
1. Use FCEUX PPU Viewer to identify tile patterns
2. Locate tile data in ROM or trace CHR RAM writes
3. Extract with `find_ff1_monster_tiles.py` or custom script

## Known Issues & Limitations

### Unresolved Fields
All 20 MonsterStats bytes are now identified (see the struct above). The last
"unknown" byte (E) was pinned as the attack element by cross-referencing the
gamercorner guide. Remaining open items are the treasure gold-chest amounts
(item ids 0x6c-0xff) and the 0x12-0x15 special item ids.

### Graphics Extraction Challenges (resolved)
- Enemy sprite CHR is in PRG (bank 07/08, 0x1c010+), loaded to CHR RAM at battle
- extract_monster_sprites.py decodes all 123 sprites in color (see that script)
- Requires runtime memory capture or tile mapping

### String Fragmentation
- Intro text found but fragmented into substrings
- Need to identify string concatenation logic
- May require code analysis in Ghidra

## Future Development

### Immediate Tasks
1. Decode remaining unknown fields using community guides
2. Extract monster sprites using runtime memory capture
3. Map complete bitvector meanings (all bits documented)
4. Extract intro text with proper concatenation

### Long-term Goals
1. Complete Ghidra disassembly with labeled functions
2. Document battle system mechanics
3. Extract music and sound effects
4. Create comprehensive FF1 data documentation

## Analysis Workflow

### Initial Discovery Phase (Completed)
1. ✅ Used FCEUX to locate character tiles
2. ✅ Found monster names via name table inspection
3. ✅ Built character encoding dictionary
4. ✅ Located monster name region (0x2d5f0)
5. ✅ Located monster stats region (0x30530)

### Data Extraction Phase (Completed)
1. ✅ Wrote string extraction script
2. ✅ Extracted all 128 monster names
3. ✅ Defined MonsterStats struct in ImHex
4. ✅ Validated struct with known monster data
5. ✅ Automated extraction with Python

### Current Phase (In Progress)
1. 🔄 Decoding unknown struct fields
2. 🔄 Extracting monster sprites
3. ⏸️ Intro text extraction
4. ⏸️ Ghidra disassembly

## Reference Documentation

See `docs/README.md` for:
- Detailed analysis notes
- ImHex pattern definitions
- Example monster data tables
- Reference links to ROM/RAM maps

## Notes for Claude Code

When working with this project:
- ROM offsets are well-documented - use them as ground truth
- Scripts are modular - `monster_names.py` is imported by other scripts
- Character encoding table is critical for all text extraction
- FCEUX debugger is better than Ghidra for NES-specific work
- Unknown fields should be marked clearly, not guessed
- Cross-reference findings with Game Corner monster guide
