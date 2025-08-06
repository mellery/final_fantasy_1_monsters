import os
import sys
from tkinter import Image
import numpy as np
from PIL import Image
from create_image_grid import create_image_grid

def show_tile(tile, location=0, save_image=False):
    tile[tile == 0] = 0  # Set 0 values to white for better visibility
    tile[tile == 1] = 85  # Set 1 values to light gray
    tile[tile == 2] = 170  # Set 2 values to dark gray
    tile[tile == 3] = 255  # Set 3 values to black
    normalized_array = tile.astype(np.uint8)  # Convert to 8-bit integers

    image = Image.fromarray(normalized_array)

    # image.show()
    if save_image:
        if not os.path.exists('output'):
            os.makedirs('output')
        image.save(f"./output/{str(location)}_tile.png")

    return image


# https://www.dustmop.io/blog/2015/04/28/nes-graphics-part-1/
def address_to_tile(address, offset=0, save_image=False):
    #print(address)
    tile = np.zeros((8, 8), dtype=int)
    for i in range(8):
        lower = address[i] 
        upper = address[i + 8]
        for j in range(8):
            tile[i, j] = ((lower >> (7 - j)) & 1) + (((upper >> (7 - j)) & 1) << 1)
    #print(tile)
    image = show_tile(tile, offset, save_image)
    return tile, image


def find_tiles(file_bytes):
    for index, byte in enumerate(file_bytes):
        hex_byte = bytes([byte])


def factor_pairs(n):
    pairs = []
    for i in range(1, int(n**0.5) + 1):
        if n % i == 0:
            pairs.append((i, n // i))
    print(pairs)
    return pairs


def minimal_difference_pair(n):
    pairs = factor_pairs(n)
    if not pairs:
        return None
    return min(pairs, key=lambda x: abs(x[0] - x[1]))

def main():
    rom_filename = sys.argv[1] if len(sys.argv) > 1 else 'Final Fantasy (USA).nes'

    try:
        # Open the file in binary mode
        offset = 0
        with open(rom_filename, 'rb') as file:
            # Read the entire file as bytes
            #file_bytes = file.read()
            # find_tiles(file_bytes)

            start_loc = 0x1c000+32
            file.seek(start_loc)

            images = []

            while chunk := file.read(16):  # Read 16 bytes at a time
                address = []
                
                for b in chunk:
                    address.append(b)
                #print(address)
                address_to_tile(address, offset)
                offset += 16
                tile, image = address_to_tile(address, offset)
                images.append(image)

            print(f"read {len(images)} tiles")
            grid_size = minimal_difference_pair(len(images))
            grid_size = (4096, 4)
            print(f"grid size: {grid_size}")

            current_address = start_loc
            x = 0
            while 0 < len(images) - x:
                x, current_address = process_terrain_tile(images, x, current_address, False)

                x, current_address = process_single_tile(images, x, current_address, False)

                x, current_address = process_monster_tile(images, x, current_address)

                x, current_address = process_monster_tile(images, x, current_address)

                x, current_address = process_medium_monster_tile(images, x, current_address)

                x, current_address = process_medium_monster_tile(images, x, current_address)

                x, current_address = process_footer(images, x, current_address, False)

                x, current_address = process_single_tile(images, x, current_address, False)

                if current_address >= 0x24020:
                    break

            #create_image_grid(images, 'tiles.png', grid_size=grid_size)

    except FileNotFoundError:
        print(f"Error: ROM file '{rom_filename}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading ROM file: {e}")
        sys.exit(1)


def process_terrain_tile(images, x, current_address, create_grid=True):
    grid_size = (4, 4)
    if create_grid:
        create_image_grid(images[x:], f'tiles_{current_address:08x}.png', grid_size=grid_size)
    x += grid_size[0] * grid_size[1]
    current_address += grid_size[0] * grid_size[1] * 16
    return x, current_address

def process_single_tile(images, x, current_address, create_grid=False):
    grid_size = (1, 1)
    if create_grid:
        create_image_grid(images[x:], f'tiles_{current_address:08x}.png', grid_size=grid_size)
    x += grid_size[0] * grid_size[1]
    current_address += grid_size[0] * grid_size[1] * 16
    return x, current_address

def process_monster_tile(images, x, current_address, create_grid=True):
    grid_size = (4, 4)
    if create_grid:
        create_image_grid(images[x:], f'tiles_{current_address:08x}.png', grid_size=grid_size)
    x += grid_size[0] * grid_size[1]
    current_address += grid_size[0] * grid_size[1] * 16
    return x, current_address

def process_medium_monster_tile(images, x, current_address, create_grid=True):
    grid_size = (6, 6)
    if create_grid:
        create_image_grid(images[x:], f'tiles_{current_address:08x}.png', grid_size=grid_size)
    x += grid_size[0] * grid_size[1]
    current_address += grid_size[0] * grid_size[1] * 16
    return x, current_address

def process_footer(images, x, current_address, create_grid=False):
    grid_size = (1, 6)
    if create_grid:
        create_image_grid(images[x:], f'tiles_{current_address:08x}.png', grid_size=grid_size)
    x += grid_size[0] * grid_size[1]
    current_address += grid_size[0] * grid_size[1] * 16
    return x, current_address


if __name__ == "__main__":
    main()
