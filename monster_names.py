characters = {
    b'\x80': "0",  # TODO: how to get this programmatically?
    b'\x81': "1",
    b'\x82': "2",
    b'\x83': "3",
    b'\x84': "4",
    b'\x85': "5",
    b'\x86': "6",
    b'\x87': "7",
    b'\x88': "8",
    b'\x89': "9",
    b'\x8a': "A",
    b'\x8b': "B",
    b'\x8c': "C",
    b'\x8d': "D",
    b'\x8e': "E",
    b'\x8f': "F",
    b'\x90': "G",
    b'\x91': "H",
    b'\x92': "I",
    b'\x93': "J",
    b'\x94': "K",
    b'\x95': "L",
    b'\x96': "M",
    b'\x97': "N",
    b'\x98': "O",
    b'\x99': "P",
    b'\x9a': "Q",
    b'\x9b': "R",
    b'\x9c': "S",
    b'\x9d': "T",
    b'\x9e': "U",
    b'\x9f': "V",
    b'\xa0': "W",
    b'\xa1': "X",
    b'\xa2': "Y",
    b'\xa3': "Z",
    b'\xa4': "a",
    b'\xa5': "b",
    b'\xa6': "c",
    b'\xa7': "d",
    b'\xa8': "e",
    b'\xa9': "f",
    b'\xaa': "g",
    b'\xab': "h",
    b'\xac': "i",
    b'\xad': "j",
    b'\xae': "k",
    b'\xaf': "l",
    b'\xb0': "m",
    b'\xb1': "n",
    b'\xb2': "o",
    b'\xb3': "p",
    b'\xb4': "q",
    b'\xb5': "r",
    b'\xb6': "s",
    b'\xb7': "t",
    b'\xb8': "u",
    b'\xb9': "v",
    b'\xba': "w",
    b'\xbb': "x",
    b'\xbc': "y",
    b'\xbd': "z",
    b'\xbe': "'",
    b'\xbf': ",",
    b'\xc0': ".",
    b'\xc1': " ",
    b'\xc2': "-",
    b'\xc3': "..",
    b'\xc4': "!",
    b'\xc5': "?"
}


def get_names(file_bytes):
    result_string = ""
    start_offset = 0x2d5f0  #TODO: magic number
    names = []
    for index, byte in enumerate(file_bytes[start_offset:], start=start_offset):
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


# Open the file in binary mode
with open('Final Fantasy (USA).nes', 'rb') as file:  # TODO: command line argument
    # Read the entire file as bytes
    file_bytes = file.read()

# Call the find_strings function
get_names(file_bytes)
