from cairosvg import svg2png

def convert_svg_to_png(svg_content, png_file_path, dpi=300):
    """
    Converts SVG content to a PNG file.

    Args:
    - svg_content (str): The SVG content as a string.
    - png_file_path (str): The path to save the output PNG file.
    - dpi (int): The DPI for the output image.
    """
    try:
        svg2png(bytestring=svg_content.encode('utf-8'), write_to=png_file_path, dpi=dpi)
        print(f"Successfully converted SVG to {png_file_path}")
    except Exception as e:
        print(f"Conversion failed: {e}")