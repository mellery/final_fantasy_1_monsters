characters = {}

#'''
characters[b'00000'] = 'M'
characters[b'000010'] = '*'
characters[b'000011000'] = 'J'
characters[b'0000110010'] = '8'
characters[b'0000110011'] = '6'
characters[b'00001101'] = '-'
characters[b'0000111'] = 'V'
characters[b'0001'] = 'R'
characters[b'00100'] = 'C'
characters[b'001010'] = 'B'
characters[b'001011000'] = 'X'
characters[b'0010110010'] = '5'
characters[b'0010110011'] = '3'
characters[b'001011010'] = '.'
characters[b'00101101100'] = '[full title:]'
characters[b'00101101101'] = '7'
characters[b'0010110111'] = 'Z'
characters[b'0010111'] = 'K'
characters[b'0011'] = 'N'
characters[b'010'] = ' '
characters[b'011000'] = 'Y'
characters[b'011001'] = 'P'
characters[b'01101'] = 'D'
characters[b'0111'] = 'S'
characters[b'1000'] = 'I'
characters[b'1001'] = 'O'
characters[b'1010'] = 'A'
characters[b'1011'] = 'T'
characters[b'110000'] = 'W'
characters[b'110001'] = 'G'
characters[b'11001'] = 'L'
characters[b'11010'] = '\n'#'[line]'
characters[b'110110'] = 'F'
characters[b'110111000'] = '1'
characters[b'11011100100'] = '4'
characters[b'11011100101'] = '2'
characters[b'1101110011'] = '9'
characters[b'11011101'] = ','
characters[b'1101111000'] = '0'
characters[b'11011110010000'] = ':'
characters[b'11011110010001'] = '!'
characters[b'1101111001001'] = '/'
characters[b'110111100101'] = ';'
characters[b'11011110011'] = 'Q'
characters[b'110111101'] = '&'
characters[b'11011111'] = "'"
characters[b'11100'] = 'H'
characters[b'111010'] = '\n\n'#'[end]'
characters[b'111011'] = 'U'
characters[b'1111'] = 'E'
#'''
#player answers
'''
characters[b'0000'] = 'L'
characters[b'000100'] = 'F'
characters[b'0001010000'] = '2'
characters[b'00010100010'] = '!'
characters[b'000101000110'] = ','
characters[b'000101000111'] = '$'
characters[b'000101001'] = 'l'
characters[b'00010101'] = 'Z'
characters[b'0001011000'] = 'c'
characters[b'0001011001'] = '6'
characters[b'000101101'] = 'w'
characters[b'000101110'] = 'g'
characters[b'000101111'] = '-'
characters[b'000110'] = 'K'
characters[b'000111'] = 'o'
characters[b'0010'] = 'O'
characters[b'0011'] = 'P'
characters[b'0100'] = 'T'
characters[b'01010'] = 'D'
characters[b'010110'] = 's'
characters[b'010111'] = 'u'
characters[b'01100'] = '+'
characters[b'01101000'] = 'X'
characters[b'01101001'] = '.'
characters[b'011010100'] = '&'
characters[b'0110101010'] = '*'
characters[b'0110101011'] = "'"
characters[b'011010110000'] = 'd'
characters[b'011010110001'] = 'b'
characters[b'011010110010'] = 'k'
characters[b'011010110011'] = 'j'
characters[b'011010110100'] = '5'
characters[b'011010110101'] = '/'
characters[b'011010110110'] = '9'
characters[b'011010110111'] = '7'
characters[b'011010111000'] = 'x'
characters[b'011010111001'] = 'v'
characters[b'011010111010'] = 'z'
characters[b'011010111011'] = 'y'
characters[b'011010111100'] = 'p'
characters[b'011010111101'] = 'n'
characters[b'011010111110'] = 'r'
characters[b'011010111111'] = 'q'
characters[b'011011'] = 'i'
characters[b'0111'] = 'N'
characters[b'1000'] = 'A'
characters[b'1001'] = 'R'
characters[b'10100'] = 'C'
characters[b'1010100'] = 'U'
characters[b'1010101000'] = '1'
characters[b'1010101001'] = '0'
characters[b'1010101010'] = '4'
characters[b'1010101011'] = '3'
characters[b'10101011000'] = 'Q'
characters[b'10101011001'] = '8'
characters[b'10101011010'] = 'm'
characters[b'10101011011'] = 'f'
characters[b'10101011100'] = 't'
characters[b'101011'] = 'P'
characters[b'101100'] = 'B'
characters[b'1011010'] = '[alternate answer:]'
characters[b'1011011'] = 'W'
characters[b'101110'] = 'Y'
characters[b'10111100'] = 'h'
characters[b'10111101'] = 'J'
characters[b'1011111'] = 'V'
characters[b'11000'] = 'I'
characters[b'110010'] = 'H'
characters[b'110011'] = 'G'
characters[b'110100'] = 'a'
characters[b'110101'] = 'M'
characters[b'11011'] = 'E'
characters[b'11100'] = 'e'
characters[b'11101'] = 'S'
characters[b'1111'] = '\n'#'[end]'
'''

def find_huffman(file_bytes):
    binary_string = ''.join(f'{byte:08b}' for byte in file_bytes)
    result = ""
    i = 0
    keys = {k.decode(): v for k, v in characters.items()}
    max_key_len = max(len(k) for k in keys)
    while i < len(binary_string):
        matched = False
        for l in range(1, max_key_len + 1):
            key = binary_string[i:i+l]
            if key in keys:
                result += keys[key]
                i += l
                matched = True
                break
        if not matched:
            result += '?'
            i += 1  # skip unknown
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
