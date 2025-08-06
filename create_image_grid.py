from PIL import Image
import os
import glob

def create_image_grid(images, output_path, grid_size=(10, 10)):
    """
    Creates a single image from a list of images arranged in a grid.

    Args:
        image_paths (list): A list of paths to the input images.
        output_path (str): The path to save the output grid image.
        grid_size (tuple): A tuple representing the grid dimensions (rows, cols).
    """
    

    img_width, img_height = images[0].size

    # Create a new image to hold the grid
    grid_width = grid_size[1] * img_width
    grid_height = grid_size[0] * img_height
    grid_image = Image.new('RGB', (grid_width, grid_height))

    # Paste images into the grid
    for index, img in enumerate(images):
        row = index // grid_size[1]
        col = index % grid_size[1]
        x_offset = col * img_width
        y_offset = row * img_height
        grid_image.paste(img, (x_offset, y_offset))

        if index >= grid_size[0] * grid_size[1] - 1:
            break

    # Save the new image
    grid_image.save(output_path)
    print(f"Image grid saved to {output_path}")

if __name__ == '__main__':
    # This is an example of how to use the function.
    # It assumes you have a directory named 'output' with your 100 images.
    # You might need to change 'output/*.png' to match your image files.
    image_files = sorted(glob.glob('output/*.png'))

    if len(image_files) >= 100:
        create_image_grid(image_files[:100], 'image_grid.png')
    else:
        print(f"Found {len(image_files)} images, but 100 are needed for a 10x10 grid.")

