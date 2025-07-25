import os
import sys
from tkinter import Image
import numpy as np
from PIL import Image
from pyparsing import nums
from create_image_grid import create_image_grid
from nes_color_converter import NES_PALETTE, hex_to_rgb


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


def show_pallet(pallet, location=0, save_image=False):
    #print(f"Showing pallet at location {location}")
    #print(f"Pallet colors: {pallet}")

    image = Image.fromarray(pallet.astype(np.uint8))

    # image.show()
    if save_image:
        if not os.path.exists('output'):
            os.makedirs('output')
        image.save(f"./output/{str(location)}_pallet.png")

    return image


def address_to_pallet(address, offset=0, save_image=False):
    #print(address[0])
    tile = np.zeros((8, 8, 3), dtype=int)
    color = hex_to_rgb(str(address))
    for i in range(8):
        for j in range(8):
            tile[i, j] = color
    
    #print(tile)
    image = show_pallet(tile, offset, save_image)
    return tile, image


def main():
    rom_filename = sys.argv[1] if len(sys.argv) > 1 else 'Final Fantasy (USA).nes'

    try:
        # Open the file in binary mode
        offset = 0
        with open(rom_filename, 'rb') as file:
            # Read the entire file as bytes
            #file_bytes = file.read()
            #print(f"Read {len(file_bytes)} bytes from ROM file.")

            images = []
            file.seek(200496)  # Adjust the offset to where the pallet data starts

            while chunk := file.read(4):  # Read 4 bytes at a time
                address = []

                for b in chunk:
                    address.append(hex(b))
                
                # Check if all bytes are valid NES color indices
                if all(int(b, 16) < len(NES_PALETTE) for b in address):
                    for i in range(len(address)):
                        tile, image = address_to_pallet(address[i], offset+1)
                        images.append(image)
                else:
                    # If not all bytes are valid NES color indices, fill with a default color
                    for i in range(len(address)):
                        # Use a default color (e.g., black) for invalid indices
                        address[i] = "FF"  # set invalid
                        tile, image = address_to_pallet(address[i], offset+i)
                    images.append(image)

                offset += 4
                
            print(f"read {len(images)} tiles")
            grid_size = minimal_difference_pair(len(images))
            #grid_size = (1,4)
            print(f"grid size: {grid_size}")

            create_image_grid(images, 'pallets.png', grid_size=grid_size)

    except FileNotFoundError:
        print(f"Error: ROM file '{rom_filename}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading ROM file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
