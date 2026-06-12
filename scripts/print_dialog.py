"""Dump all dialog entries from Final Fantasy (USA) by walking the pointer table.

Dialog lives in the bank at file offset 0x28010 (CPU $8000). The bank starts
with a table of 256 little-endian pointers; each points at a string of
.tbl-encoded text (DTE pairs + single characters) ending with 0x00.
0x05 is a line break (mapped via the *05 entry in final_fantasy.tbl).
"""
import os
import struct
import sys
from load_tbl import generate_character_map

TBL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools', 'final_fantasy.tbl')
characters = generate_character_map(TBL_PATH)

POINTER_TABLE = 0x28010  # file offset of the pointer table (after iNES header)
NUM_ENTRIES = 256
CPU_BASE = 0x8000        # CPU address the bank is mapped at


def decode_string(data, offset):
    """Decode a 0x00-terminated FF1 string at the given file offset."""
    parts = []
    while offset < len(data):
        byte = data[offset]
        if byte == 0x00:
            break
        key = bytes([byte])
        if key in characters:
            parts.append(characters[key])
        else:
            parts.append(f'[{byte:02X}]')  # unmapped control code
        offset += 1
    return ''.join(parts)


def get_dialog(data):
    """Return a list of (file_offset, text) for all dialog entries."""
    entries = []
    for i in range(NUM_ENTRIES):
        ptr = struct.unpack_from('<H', data, POINTER_TABLE + i * 2)[0]
        offset = POINTER_TABLE + (ptr - CPU_BASE)
        entries.append((offset, decode_string(data, offset)))
    return entries


def main():
    rom_filename = sys.argv[1] if len(sys.argv) > 1 else '../roms/Final Fantasy (USA).nes'

    try:
        with open(rom_filename, 'rb') as file:
            data = file.read()
    except FileNotFoundError:
        print(f"Error: ROM file '{rom_filename}' not found")
        sys.exit(1)

    for i, (offset, text) in enumerate(get_dialog(data)):
        indented = text.rstrip('\n').replace('\n', '\n     ')
        print(f"{i:3d} (0x{offset:05x}): {indented}")
        print()


if __name__ == "__main__":
    main()
