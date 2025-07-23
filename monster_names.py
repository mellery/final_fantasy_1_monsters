import sys
from ff1_utils import generate_character_map

characters = generate_character_map()


def get_names(file_bytes):
    result_string = ""
    start_offset = 0x2d5f0  # TODO: magic number
    names = []
    for i, byte in enumerate(file_bytes[start_offset:], start=start_offset):
        hex_byte = bytes([byte])
        if hex_byte in characters:
            result_string += characters[hex_byte]
        else:
            if result_string and len(result_string) > 2:
                names.append(result_string)
                result_string = ""
                if len(names) == 128:
                    return names
    if result_string and len(result_string) > 2:
        names.append(result_string)
    return names


def main():
    rom_filename = sys.argv[1] if len(sys.argv) > 1 else 'Final Fantasy (USA).nes'

    try:
        # Open the file in binary mode
        with open(rom_filename, 'rb') as file:
            # Read the entire file as bytes
            file_bytes = file.read()
            names = get_names(file_bytes)
            for i, name in enumerate(names):
                print(f"{i:3d}: {name}")
    except FileNotFoundError:
        print(f"Error: ROM file '{rom_filename}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading ROM file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
