#!/usr/bin/env python3
"""Remove background from an image using rembg library."""

import sys
import os

def remove_background(input_path, output_path=None):
    """Remove background from image and save result."""
    try:
        from rembg import remove
        from PIL import Image
    except ImportError:
        print("Installing required packages...")
        os.system(f"{sys.executable} -m pip install rembg pillow onnxruntime")
        from rembg import remove
        from PIL import Image

    if output_path is None:
        name, ext = os.path.splitext(input_path)
        output_path = f"{name}_nobg.png"

    with open(input_path, "rb") as inp:
        input_data = inp.read()

    output_data = remove(input_data)

    with open(output_path, "wb") as out:
        out.write(output_data)

    print(f"Background removed: {output_path}")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python remove_bg.py <input_image> [output_image]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    remove_background(input_file, output_file)
