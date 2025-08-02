from load_tbl import load_tbl_file

# Load character mapping from jeopardy_questions.tbl using binary format
characters = load_tbl_file('jeopardy_questions.tbl', binary=True)

def find_huffman(file_bytes):
    binary_string = ''.join(f'{byte:08b}' for byte in file_bytes)
    result = ""
    i = 0
    
    # Convert byte sequences (which are encoded binary strings) back to strings for matching
    binary_patterns = {}
    for byte_seq, text in characters.items():
        # In binary mode, byte_seq is the binary string encoded as ASCII bytes
        binary_key = byte_seq.decode('ascii')
        binary_patterns[binary_key] = text
    
    if not binary_patterns:
        print("No character mappings loaded from TBL file")
        return
    
    # Debug: show a few patterns
    print(f"Loaded {len(binary_patterns)} patterns")
    for pattern, text in binary_patterns.items():
        if text == ' ':
            print(f"Space pattern: '{pattern}' -> '{text}'")
        elif pattern.startswith('11010'):
            print(f"Pattern starting with 11010: '{pattern}' -> '{text}'")
        elif '[' in text:
            print(f"Pattern with brackets: '{pattern}' -> '{text}'")
    
    max_key_len = max(len(k) for k in binary_patterns.keys())
    
    debug_count = 0
    while i < len(binary_string):
        matched = False
        # Try longest matches first to handle overlapping patterns correctly
        for l in range(max_key_len, 0, -1):
            key = binary_string[i:i+l]
            if key in binary_patterns:
                result += binary_patterns[key]
                i += l
                matched = True
                break
        if not matched:
            # Debug: show what pattern failed to match
            if debug_count < 5:  # Only show first few mismatches
                context = binary_string[i:i+20]  # Show 20 bits of context
                print(f"No match at position {i}: '{context}' (starting with '{binary_string[i:i+10]}')")
                debug_count += 1
            result += '?'
            i += 1  # skip unknown bit
    print(result)
        

import sys

def main():
    rom_filename = sys.argv[1] if len(sys.argv) > 1 else 'Jeopardy! (U).nes'
    
    try:
        # Open the file in binary mode
        with open(rom_filename, 'rb') as file:
            # Read the entire file as bytes
            file_bytes = file.read()
            find_huffman(file_bytes)
    except FileNotFoundError:
        print(f"Error: ROM file '{rom_filename}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading ROM file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
