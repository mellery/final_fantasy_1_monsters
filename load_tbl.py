def load_tbl_file(tbl_file='final_fantasy.tbl', binary=False):
    """Load character mapping from a .tbl file following the complete TBL specification
    
    Args:
        tbl_file: Path to the .tbl file
        binary: If True, expect binary sequences instead of hex (non-standard extension)
                In binary mode, '[' and ']' characters are allowed for Huffman codes
    """
    characters = {}
    
    try:
        with open(tbl_file, 'r', encoding='utf-8-sig') as f:  # Handle BOM
            for line_num, line in enumerate(f, 1):
                line = line.rstrip('\n\r')  # Only remove line endings
                
                # Skip blank lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Handle special prefixes
                if line.startswith('$') or line.startswith('!'):
                    # Control codes, table switching - skip for now
                    continue
                
                # Handle end tokens (/PATTERN=TEXT)
                if line.startswith('/'):
                    line = line[1:]  # Remove the / prefix and process normally
                
                # Handle newline entries (*HEX/*BIN format - legacy support)
                if line.startswith('*'):
                    val = line[1:].strip()
                    try:
                        if binary:
                            if not all(c in '01' for c in val):
                                print(f"Warning: Invalid binary sequence at line {line_num}: {val}")
                                continue
                            # For binary mode, store the binary string directly as bytes
                            byte_sequence = val.encode('ascii')
                        else:
                            if len(val) % 2 != 0:
                                print(f"Warning: Odd-length hex sequence at line {line_num}: {val}")
                                continue
                            byte_sequence = bytes.fromhex(val)
                        characters[byte_sequence] = '\n'
                    except ValueError:
                        print(f"Warning: Invalid {'binary' if binary else 'hex'} sequence at line {line_num}: {val}")
                        continue
                
                # Handle normal entries (HEX=TEXT or BIN=TEXT)
                elif '=' in line:
                    val_part, text_part = line.split('=', 1)
                    val_part = val_part.strip()
                    
                    # Validate value part
                    if not val_part:
                        print(f"Warning: Blank {'binary' if binary else 'hex'} sequence at line {line_num}")
                        continue
                    
                    # Check for invalid characters in text part (skip in binary mode for Huffman codes)
                    if not binary and ('[' in text_part or ']' in text_part):
                        print(f"Warning: Text contains invalid characters '[' or ']' at line {line_num}")
                        continue
                    
                    # Process escape sequences in text
                    text_part = text_part.replace('\\n', '\n')
                    
                    # Convert special tokens to newlines (for Huffman codes)
                    if text_part == '[line]':
                        text_part = '\n'
                    elif text_part == '[end]':
                        text_part = '\n\n'
                    
                    try:
                        if binary:
                            if not all(c in '01' for c in val_part):
                                print(f"Warning: Invalid binary sequence at line {line_num}: {val_part}")
                                continue
                            # For binary mode, store the binary string directly as bytes
                            byte_sequence = val_part.encode('ascii')
                        else:
                            if len(val_part) % 2 != 0:
                                print(f"Warning: Odd-length hex sequence at line {line_num}: {val_part}")
                                continue
                            byte_sequence = bytes.fromhex(val_part)
                        
                        # Check for duplicate sequences
                        if byte_sequence in characters:
                            print(f"Warning: Duplicate {'binary' if binary else 'hex'} sequence at line {line_num}: {val_part}")
                            continue
                            
                        characters[byte_sequence] = text_part
                    except ValueError:
                        print(f"Warning: Invalid {'binary' if binary else 'hex'} sequence at line {line_num}: {val_part}")
                        continue
                else:
                    print(f"Warning: Unrecognized syntax at line {line_num}: {line}")
                    
    except FileNotFoundError:
        print(f"Warning: {tbl_file} not found")
        return {}
    except UnicodeDecodeError:
        print(f"Warning: {tbl_file} is not valid UTF-8")
        return {}
    
    return characters

def generate_character_map(tbl_file='final_fantasy.tbl', binary=False):
    """Generate FF1 character mapping dictionary from .tbl file"""
    return load_tbl_file(tbl_file, binary)