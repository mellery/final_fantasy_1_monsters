from load_tbl import generate_character_map

characters = generate_character_map("final_fantasy.tbl")


def find_strings(file_bytes):
    result_string = ""
    start_index = 0
    for index, byte in enumerate(file_bytes):
        hex_byte = bytes([byte])
        if hex_byte in characters:
            if not result_string:
                start_index = index
            result_string += characters[hex_byte]
        else:
            if result_string and len(result_string) > 2:
                print(f"{start_index:#x}: {result_string}")
                result_string = ""
            #print(f"{hex_byte.hex()}", end=' ')
    if result_string:
        print(f"{start_index:#x}: {result_string}")


import sys

def main():
    rom_filename = sys.argv[1] if len(sys.argv) > 1 else 'Final Fantasy (USA).nes'
    
    try:
        # Open the file in binary mode
        with open(rom_filename, 'rb') as file:
            # Read the entire file as bytes
            file_bytes = file.read()
            find_strings(file_bytes)
    except FileNotFoundError:
        print(f"Error: ROM file '{rom_filename}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading ROM file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
