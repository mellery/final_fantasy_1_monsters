
# The standard sRGB representation of the 64-color NTSC NES palette.
NES_PALETTE = [
    (124, 124, 124), (0, 0, 252), (0, 0, 188), (68, 40, 188),
    (148, 0, 132), (168, 0, 32), (168, 16, 0), (136, 20, 0),
    (80, 48, 0), (0, 120, 0), (0, 104, 0), (0, 88, 0),
    (0, 64, 88), (0, 0, 0), (0, 0, 0), (0, 0, 0),

    (188, 188, 188), (0, 120, 248), (0, 88, 248), (104, 68, 252),
    (216, 0, 204), (228, 0, 88), (248, 56, 0), (228, 92, 16),
    (172, 124, 0), (0, 184, 0), (0, 168, 0), (0, 168, 68),
    (0, 136, 136), (0, 0, 0), (0, 0, 0), (0, 0, 0),

    (248, 248, 248), (60, 188, 252), (104, 136, 252), (152, 120, 248),
    (248, 120, 248), (248, 88, 152), (248, 120, 88), (252, 160, 68),
    (248, 184, 0), (184, 248, 24), (88, 216, 84), (88, 248, 152),
    (0, 232, 216), (120, 120, 120), (0, 0, 0), (0, 0, 0),

    (252, 252, 252), (164, 228, 252), (184, 184, 248), (216, 184, 248),
    (248, 184, 248), (248, 164, 192), (240, 208, 176), (252, 224, 168),
    (248, 216, 120), (216, 248, 120), (184, 248, 184), (184, 248, 216),
    (0, 252, 252), (248, 216, 248), (0, 0, 0), (0, 0, 0)
]

def hex_to_rgb(hex_color_index):
  """Converts an NES hex color index to an RGB tuple."""
  decimal_index = int(hex_color_index, 16)
  #print(f"hex_color_index: {hex_color_index}, decimal_index: {int(hex_color_index, 16)}")
  if 0 <= decimal_index < len(NES_PALETTE):
    rgb_value = NES_PALETTE[decimal_index]
    #print(f"The NES color ${hex_color_index} is RGB: {rgb_value} (hex: #{rgb_value[0]:02x}{rgb_value[1]:02x}{rgb_value[2]:02x})")
    return rgb_value
  else:
    return (0, 0, 0)  # Return black for invalid indices


if __name__ == "__main__":
      
    # The hex value from the palette editor
    hex_value = "2A"
    rgb_value = hex_to_rgb(hex_value)

    if rgb_value:
        print(f"The NES color ${hex_value} is RGB: {rgb_value} (hex: #{rgb_value[0]:02x}{rgb_value[1]:02x}{rgb_value[2]:02x})")
    else:
        print(f"Invalid NES color index: ${hex_value}")
