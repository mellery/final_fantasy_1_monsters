def generate_character_map(start_hex=0x80):
    """Generate FF1 character mapping dictionary starting from given hex value"""
    characters = {}
    
    # Numbers 0-9
    for i, char in enumerate("0123456789"):
        characters[bytes([start_hex + i])] = char
    
    # Uppercase A-Z
    for i, char in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        characters[bytes([start_hex + 10 + i])] = char
    
    # Lowercase a-z
    for i, char in enumerate("abcdefghijklmnopqrstuvwxyz"):
        characters[bytes([start_hex + 36 + i])] = char
    
    # Special characters
    special_chars = ["'", ",", ".", " ", "-", "..", "!", "?"]
    for i, char in enumerate(special_chars):
        characters[bytes([start_hex + 62 + i])] = char
    
    return characters