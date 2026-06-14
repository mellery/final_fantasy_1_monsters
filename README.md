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
├── scripts/                  # Python analysis scripts
│   ├── monster_names.py     # Extract monster names
│   ├── print_monsters.py    # Extract complete monster data
│   ├── find_strings.py      # General string finder
│   ├── find_ff1_monster_tiles.py  # Monster sprite extraction
│   ├── find_tiles.py        # General tile finder
│   ├── find_pallets.py      # Palette finder
│   ├── find_huffman.py      # Huffman encoding analyzer
│   ├── load_tbl.py          # Table file loader
│   ├── nes_color_converter.py  # NES palette converter
│   └── create_image_grid.py # Image grid generator
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

```c
struct MonsterStats {
    u16 exp;           // Experience points
    u16 gold;          // Gold dropped
    u16 HP;            // Hit points
    u8 morale;         // Morale stat
    u8 unknown1;       // Possibly AI
    u8 unknown2;       // Possibly evade
    u8 absorb;         // Damage absorption
    u8 hits;           // Number of attacks
    u8 unknown5;       // Possibly hit rate
    u8 dmg;            // Damage per hit
    u8 unknown6;       // Possibly crit rate
    u8 unknown7;       // Unknown
    u8 unknown8;       // Possibly attack ailment
    u8 family;         // Monster family bitvector
    u8 unknown10;      // Possibly magic defense
    u8 weak;           // Elemental weakness bitvector
    u8 resist;         // Elemental resistance bitvector
};
```

### ROM Offsets
- **Monster Names**: 0x2d5f0 to 0x2d951
- **Monster Stats**: 0x30530 (128 structs × 20 bytes)
- **Character Tiles**: PPU $80

### Character Encoding
Custom character encoding map (0x80-0xC5) for FF1's text system:
- Located in `tools/final_fantasy.tbl`
- Used by string extraction scripts

### Element & Family Bitvectors

**Element Encoding** (weak/resist fields):
```
0x10 = Fire
0x20 = Cold
0x40 = Lightning
0x80 = Earth
```

**Family Encoding**:
```
0x02 = Dragon
0x04 = Giant
0x20 = Aquatic
0x40 = Spellcaster
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

### Extract Monster Sprites
```bash
python3 find_ff1_monster_tiles.py
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
- Monster stats structure decoded (17/20 fields identified)
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
- Monster weak/resist decoded with the element bitfield (print_monsters.py)
- Element bitfield fully decoded (Status/Poison/Time/Death/Fire/Ice/Lit/Earth)

### In Progress 🔄
- Unknown fields in monster stats (5 fields remaining)
- Location->zone mapping (overworld grid + per-dungeon domain assignment)
- Treasure gold-chest amounts (ids 0x6c-0xff) and the 0x12-0x15 special items
- Shop town/type labels and clinic/caravan price slots
- Weapon/armor category words (second word from icon tile)

### TODO ⏸️
- Character class / level-up / EXP tables
- Maps (RLE-compressed overworld + town/dungeon)
- Extract music and sound effects
- Map complete game data structures in Ghidra

## Reference Materials

### ROM/RAM Maps
- [Final Fantasy ROM Map](https://datacrystal.tcrf.net/wiki/Final_Fantasy/ROM_map)
- [Final Fantasy RAM Map](https://datacrystal.tcrf.net/wiki/Final_Fantasy/RAM_map)
- [Game Corner Monster Guide](https://guides.gamercorner.net/ff/monsters/)

### NES Development
- [6502 Instruction Reference](https://www.nesdev.org/obelisk-6502-guide/reference.html)
- [NES Cart Database](https://nescartdb.com/profile/view/715/final-fantasy)
- [Writing NES Disassembler](https://medium.com/hard-mode/nes-emulator-writing-a-disassembler-and-memory-viewer-4727e76de57)

## Example Monster Data

```
NAME      HP   GOLD  EXP   DMG  HIT  FAM     WEAK      RESIST
IGUANA    92   50    153   18   1    Dragon  -         -
AGAMA     296  1200  2472  31   2    Dragon  Cold      Fire
SAURIA    196  658   1977  30   1    Dragon  -         -
GIANT     240  879   879   38   1    Giant   -         -
FrGIANT   336  1752  1752  60   1    Giant   Fire      Cold
R.GIANT   300  1506  1506  73   1    Giant   Cold      Fire
SAHAG     28   30    30    10   1    Aquatic Lightning  Fire/Earth
```

## Notes

- Ghidra disassembly attempted but FCEUX debugger proved more effective for initial analysis
- Character tiles start at PPU $80 (verified in FCEUX PPU Viewer)
- IMP monster verified as bytes 92 96 99 in name table
- Some monster names have extra characters (e.g., "PIMP" instead of "IMP")

## License & Usage
This is a reverse engineering project for educational and preservation purposes. All game content is property of Square Enix.
