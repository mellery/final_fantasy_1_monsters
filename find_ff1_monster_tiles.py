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
                # Check if we're near the end where larger monsters are located
                if current_address >= 0x22570:  # Try original detection address
                
                    # Process terrain first, then large monsters
                    #print(f"Processing terrain tile at address {current_address:08x}")
                    x, current_address = process_terrain_tile(images, x, current_address, False)

                    print(f"Processing single tile at address {current_address:08x}")
                    x, current_address = process_single_tile(images, x, current_address, False)
                    
                    print(f"Processing Kary monster tile at address {current_address:08x}")
                    x, current_address = process_kari_monster_tile(images, x, current_address, True)
                    print(f"Processing Lich monster tile at address {current_address:08x}")
                    x, current_address = process_lich_monster_tile(images, x, current_address, True)
                    
                    x, current_address = process_footer(images, x, current_address, False)
                    x, current_address = process_terrain_tile(images, x, current_address, False)

                    print(f"Processing Kraken monster tile at address {current_address:08x}")
                    x, current_address = process_kraken_monster_tile(images, x, current_address, True)
                    
                    print(f"Processing Tiamat monster tile at address {current_address:08x}")
                    x, current_address = process_tiamat_monster_tile(images, x, current_address, True)
                    
                    x, current_address = process_terrain_tile(images, x, current_address, False)
                    x, current_address = process_single_tile(images, x, current_address, False)
                    x, current_address = process_single_tile(images, x, current_address, False)
                    x, current_address = process_single_tile(images, x, current_address, False)
                    x, current_address = process_single_tile(images, x, current_address, False)
                    x, current_address = process_single_tile(images, x, current_address, False)
                    x, current_address = process_single_tile(images, x, current_address, False)
                    x, current_address = process_single_tile(images, x, current_address, False)

                    print(f"Processing Chaos monster tile at address {current_address:08x}")
                    x, current_address = process_chaos_monster_tile(images, x, current_address, True)
                    # All large monsters processed
                    break
                else:
                    # Normal processing for smaller monsters
                    x, current_address = process_terrain_tile(images, x, current_address, False)

                    x, current_address = process_single_tile(images, x, current_address, False)

                    x, current_address = process_monster_tile(images, x, current_address, True)

                    x, current_address = process_monster_tile(images, x, current_address, True)

                    x, current_address = process_medium_monster_tile(images, x, current_address, True)

                    x, current_address = process_medium_monster_tile(images, x, current_address, True)

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

def process_large_monster_tile(images, x, current_address, create_grid=True):
    # Try 8x8 for large monsters (64 tiles)
    grid_size = (8, 8)
    if create_grid:
        create_image_grid(images[x:], f'tiles_{current_address:08x}.png', grid_size=grid_size, 
                         show_grid=False, show_numbers=False, start_index=x)
    x += grid_size[0] * grid_size[1]
    current_address += grid_size[0] * grid_size[1] * 16
    return x, current_address

def process_kari_monster_tile(images, x, current_address, create_grid=True):
    """Process Kary monster with specific blank tile pattern"""
    grid_size = (8, 8)
    
    if create_grid:
        # Create a blank tile (8x8 white image)
        blank_tile = Image.new('L', (8, 8), 0)
        
        # Kary starts at tile 1681, but our debug worked with 1680, so offset by -1
        start_offset = -1
        
        # Build the tile list with blank insertions at positions 15, 39, 47-49, 55-58, 63
        selected_tiles = []
        source_tile_index = 0
        blank_positions = {15, 39, 47, 48, 49, 55, 56, 57, 58, 63}
        
        for position in range(64):
            if position in blank_positions:
                selected_tiles.append(blank_tile)
            else:
                tile_index = x + start_offset + source_tile_index
                if tile_index >= 0 and tile_index < len(images):
                    selected_tiles.append(images[tile_index])
                source_tile_index += 1
        
        create_image_grid(selected_tiles, f'tiles_{current_address:08x}.png', grid_size=grid_size, 
                         show_grid=False, show_numbers=False, start_index=0, scale_factor=1)
    
    # Advance by the number of actual tiles used (64 - 10 blanks = 54 tiles)
    tiles_used = 54
    x += tiles_used
    current_address += tiles_used * 16
    return x, current_address

def process_lich_monster_tile(images, x, current_address, create_grid=True):
    """Process Lich monster with specific blank tile pattern"""
    grid_size = (8, 8)
    
    if create_grid:
        # Create a blank tile (8x8 white image)
        blank_tile = Image.new('L', (8, 8), 0)
        
        # Build the tile list with blank insertions at positions 4-7, 14-15, 23, 31, 38-39, 47, 54-55, 63
        selected_tiles = []
        source_tile_index = 0
        blank_positions = {4, 5, 6, 7, 14, 15, 23, 31, 38, 39, 47, 54, 55, 63}
        
        for position in range(64):
            if position in blank_positions:
                selected_tiles.append(blank_tile)
            else:
                tile_index = x + source_tile_index
                if tile_index < len(images):
                    selected_tiles.append(images[tile_index])
                source_tile_index += 1
        
        create_image_grid(selected_tiles, f'tiles_{current_address:08x}.png', grid_size=grid_size, 
                         show_grid=False, show_numbers=False, start_index=0, scale_factor=1)
    
    # Advance by the number of actual tiles used (64 - 14 blanks = 50 tiles)
    tiles_used = 50
    x += tiles_used
    current_address += tiles_used * 16
    return x, current_address

def process_kraken_monster_tile(images, x, current_address, create_grid=True):
    """Process Kraken monster with specific blank tile pattern starting at x+1"""
    grid_size = (8, 8)
    
    if create_grid:
        # Create a blank tile (8x8 white image)
        blank_tile = Image.new('L', (8, 8), 0)
        
        # Start at x+1 to skip the tile that doesn't belong
        start_offset = 1
        
        # Build the tile list with blank insertions at positions 0, 6, 7, 8, 15, 16, 23, 31, 47, 55, 58
        selected_tiles = []
        source_tile_index = 0
        blank_positions = {0, 6, 7, 8, 15, 16, 24, 32, 48, 56, 58}
        
        for position in range(64):
            if position in blank_positions:
                selected_tiles.append(blank_tile)
            else:
                tile_index = x + start_offset + source_tile_index
                if tile_index < len(images):
                    selected_tiles.append(images[tile_index])
                source_tile_index += 1
        
        create_image_grid(selected_tiles, f'tiles_{current_address:08x}.png', grid_size=grid_size, 
                         show_grid=False, show_numbers=False, start_index=0, scale_factor=1)
    
    # Advance by the number of actual tiles used (64 - 11 blanks = 53 tiles) + 1 skipped tile = 54 total
    tiles_used = 54
    x += tiles_used
    current_address += tiles_used * 16
    return x, current_address

def process_tiamat_monster_tile(images, x, current_address, create_grid=True):
    """Process Tiamat monster with specific blank tile pattern"""
    grid_size = (8, 8)
    
    if create_grid:
        # Create a blank tile (8x8 white image)
        blank_tile = Image.new('L', (8, 8), 0)
        
        # Build the tile list with blank insertions at positions 0, 1, 2, 6, 7, 15, 23, 31, 39, 48, 56, 63
        selected_tiles = []
        source_tile_index = 0
        blank_positions = {0, 1, 2, 6, 7, 15, 23, 31, 39, 48, 56, 63}
        
        for position in range(64):
            if position in blank_positions:
                selected_tiles.append(blank_tile)
            else:
                tile_index = x + source_tile_index
                if tile_index < len(images):
                    selected_tiles.append(images[tile_index])
                source_tile_index += 1
        
        create_image_grid(selected_tiles, f'tiles_{current_address:08x}.png', grid_size=grid_size, 
                         show_grid=False, show_numbers=False, start_index=0, scale_factor=1)
    
    # Advance by the number of actual tiles used (64 - 12 blanks = 52 tiles)
    tiles_used = 52
    x += tiles_used
    current_address += tiles_used * 16
    return x, current_address

def process_chaos_monster_tile(images, x, current_address, create_grid=True):
    """Process Chaos monster with specific blank tile pattern"""
    grid_size = (12, 14)
    
    if create_grid:
        # Create a blank tile (8x8 white image)
        blank_tile = Image.new('L', (8, 8), 0)
        
        # Build the tile list with blank insertions at the specified positions
        selected_tiles = []
        source_tile_index = 0
        blank_positions = {0, 1, 5, 10, 11, 12, 13, 14, 15, 25, 26, 27, 28, 40, 41, 
                          42, 55, 69, 80, 85, 86, 93, 94, 95, 96, 98, 99, 100, 108, 
                          109, 110, 111, 112, 113, 114, 118, 122, 123, 124, 125, 126,
                          127, 136, 137, 138, 139, 140, 141, 145, 146, 147, 150, 151,
                          152, 153, 154, 155, 156, 157, 158, 159, 160, 161}
        
        for position in range(168):  # 12x14 = 168 tiles
            if position in blank_positions:
                selected_tiles.append(blank_tile)
            else:
                tile_index = x + source_tile_index
                if tile_index < len(images):
                    selected_tiles.append(images[tile_index])
                source_tile_index += 1
        
        create_image_grid(selected_tiles, f'tiles_{current_address:08x}.png', grid_size=grid_size, 
                         show_grid=False, show_numbers=False, start_index=0, scale_factor=1)
    
    # Calculate actual tiles used (168 total - number of blanks)
    blank_count = len({0, 1, 5, 10, 11, 12, 13, 14, 15, 25, 26, 27, 28, 40, 41, 
                      42, 55, 69, 80, 85, 86, 93, 94, 95, 96, 98, 99, 100, 108, 
                      109, 110, 111, 112, 113, 114, 118, 122, 123, 124, 125, 126,
                      127, 136, 137, 138, 139, 140, 141, 145, 146, 147, 150, 151,
                      152, 153, 154, 155, 156, 157, 158, 159, 160, 161})
    tiles_used = 168 - blank_count
    x += tiles_used
    current_address += tiles_used * 16
    return x, current_address

def process_huge_monster_tile(images, x, current_address, create_grid=False):
    # Huge monsters are 12x12
    grid_size = (12, 12)
    if create_grid:
        create_image_grid(images[x:], f'tiles_{current_address:08x}.png', grid_size=grid_size)
    x += grid_size[0] * grid_size[1]
    current_address += grid_size[0] * grid_size[1] * 16
    return x, current_address


if __name__ == "__main__":
    main()
