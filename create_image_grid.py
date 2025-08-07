from PIL import Image, ImageDraw, ImageFont
import os
import glob

def create_image_grid(images, output_path, grid_size=(10, 10), show_grid=False, show_numbers=False, start_index=0, scale_factor=1, font_size_override=None):
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

    # Scale up the image first if requested
    if scale_factor > 1:
        new_size = (grid_width * scale_factor, grid_height * scale_factor)
        grid_image = grid_image.resize(new_size, Image.NEAREST)
        # Update dimensions for drawing
        grid_width = new_size[0]
        grid_height = new_size[1]
        img_width = img_width * scale_factor
        img_height = img_height * scale_factor

    # Add red grid lines and/or numbers if requested (after scaling)
    if show_grid or show_numbers:
        draw = ImageDraw.Draw(grid_image)
        
        if show_grid:
            # Draw vertical lines
            for col in range(grid_size[1] + 1):
                x = col * img_width
                draw.line([(x, 0), (x, grid_height)], fill='red', width=2)
            
            # Draw horizontal lines  
            for row in range(grid_size[0] + 1):
                y = row * img_height
                draw.line([(0, y), (grid_width, y)], fill='red', width=2)
        
        if show_numbers:
            # Use override font size if provided, otherwise calculate based on scale factor
            if font_size_override:
                font_size = font_size_override
            else:
                font_size = max(12, int(16 * scale_factor / 4))
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", font_size)
            except:
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", font_size)
                except:
                    font = ImageFont.load_default()
            
            # Add tile numbers
            for index in range(min(len(images), grid_size[0] * grid_size[1])):
                row = index // grid_size[1]
                col = index % grid_size[1]
                x_offset = col * img_width + 4
                y_offset = row * img_height + 4
                tile_num = start_index + index
                draw.text((x_offset, y_offset), str(tile_num), fill='red', font=font)

    # Save the new image
    grid_image.save(output_path)
    #print(f"Image grid saved to {output_path}")

if __name__ == '__main__':
    # This is an example of how to use the function.
    # It assumes you have a directory named 'output' with your 100 images.
    # You might need to change 'output/*.png' to match your image files.
    image_files = sorted(glob.glob('output/*.png'))

    if len(image_files) >= 100:
        create_image_grid(image_files[:100], 'image_grid.png')
    else:
        print(f"Found {len(image_files)} images, but 100 are needed for a 10x10 grid.")

