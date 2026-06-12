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

**Key Data Structure**:
```python
@dataclass
class MonsterStats:
    exp: int          # uint16
    gold: int         # uint16
    HP: int           # uint16
    morale: int       # uint8
    unknown1: int     # uint8 - possibly AI
    unknown2: int     # uint8 - possibly evade
    absorb: int       # uint8
    hits: int         # uint8
    unknown5: int     # uint8 - possibly hit rate
    dmg: int          # uint8
    unknown6: int     # uint8 - possibly crit rate
    unknown7: int     # uint8
    unknown8: int     # uint8 - possibly attack ailment
    family: int       # uint8 - bitvector
    unknown10: int    # uint8 - possibly magic defense
    weak: int         # uint8 - element bitvector
    resist: int       # uint8 - element bitvector
```

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

## Important ROM Offsets

### Monster Data
- **Monster Names Start**: 0x2d5f0
- **Monster Names End**: 0x2d951
- **Monster Stats Start**: 0x30530
- **Monster Stats Size**: 20 bytes per monster
- **Total Monsters**: 128

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
5 fields in MonsterStats remain unknown:
- unknown1 (possibly AI/behavior)
- unknown2 (possibly evade %)
- unknown5 (possibly hit rate %)
- unknown6 (possibly crit rate %)
- unknown7, unknown8, unknown10

### Graphics Extraction Challenges
- CHR RAM (not CHR ROM) makes static extraction difficult
- Sprites loaded dynamically during gameplay
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
