#!/usr/bin/env python3
"""
Generate podcast YouTube thumbnails programmatically.

Usage:
    python generate_thumbnail.py --name "Jane Example" --designation "Founder" --company "Acme Labs" --headshot path/to/headshot.png --output thumbnail.jpg

The headshot should already have its background removed (PNG with transparency).
"""

import argparse
import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter


# === SHOW BRANDING ===
# Short show name drawn in the circular badge, with up to two small lines under it.
SHOW_BADGE = "POD"
SHOW_SUBTITLE = ("YOUR PODCAST", "NAME HERE")

# === DESIGN CONSTANTS ===
CANVAS_WIDTH = 1280
CANVAS_HEIGHT = 720
BG_COLOR = (241, 112, 31)  # Orange
CIRCLE_COLOR = (143, 135, 132)  # Grey
WHITE = (255, 255, 255)

# Layout positions
CIRCLE_CENTER = (107, 97)
CIRCLE_RADIUS = 55

# Text positions (x, y)
CONV_TEXT_POS = (175, 76)  # "In Conversation With"
NAME_START_Y = 240  # First line of name
NAME_X = 85
DESIGNATION_Y = 650
DESIGNATION_X = 85
WAVY_Y = 600

# Headshot placement
HEADSHOT_X_START = 620  # Left edge of headshot area
HEADSHOT_MAX_WIDTH = 660  # 1280 - 620
HEADSHOT_MAX_HEIGHT = 650  # Leave some margin

# Font paths (macOS)
FONT_DIR = "/System/Library/Fonts/Supplemental/"
CHALK_FONT = "/System/Library/Fonts/Supplemental/Chalkduster.ttf"
CHALK_ALT_FONT = "/System/Library/Fonts/Supplemental/ChalkboardSE.ttc"
SANS_FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
SANS_REGULAR = "/System/Library/Fonts/Supplemental/Arial.ttf"


def get_font(font_path, size):
    """Load a font, falling back to default if not found."""
    try:
        return ImageFont.truetype(font_path, size)
    except (IOError, OSError):
        try:
            return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
        except:
            return ImageFont.load_default()


def draw_wavy_line(draw, x_start, x_end, y, amplitude=4, wavelength=20, color=WHITE, width=2):
    """Draw a wavy/squiggly decorative line."""
    points = []
    for x in range(x_start, x_end):
        offset = amplitude * math.sin(2 * math.pi * x / wavelength)
        points.append((x, y + offset))

    for i in range(len(points) - 1):
        draw.line([points[i], points[i + 1]], fill=color, width=width)


def split_name_lines(name, max_chars_per_line=12):
    """Split a name into lines that fit the layout."""
    words = name.upper().split()

    if len(words) == 1:
        return [words[0]]

    # Try to split into 2 roughly equal lines
    lines = []
    current_line = ""
    for word in words:
        test_line = f"{current_line} {word}".strip()
        if len(test_line) > max_chars_per_line and current_line:
            lines.append(current_line)
            current_line = word
        else:
            current_line = test_line
    if current_line:
        lines.append(current_line)

    return lines[:3]  # Max 3 lines


def auto_size_name_font(draw, name_lines, max_width=530, max_height_per_line=120):
    """Find the largest font size that fits the name within bounds."""
    font_size = 120  # Start large

    while font_size > 30:
        font = get_font(CHALK_FONT, font_size)
        fits = True
        for line in name_lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            if text_width > max_width or text_height > max_height_per_line:
                fits = False
                break
        if fits:
            return font, font_size
        font_size -= 3

    return get_font(CHALK_FONT, 30), 30


def generate_thumbnail(name, designation, company, headshot_path, output_path):
    """Generate a podcast episode thumbnail."""

    # Create canvas
    img = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # --- Draw grey circle (show badge) ---
    cx, cy = CIRCLE_CENTER
    r = CIRCLE_RADIUS
    draw.ellipse(
        [cx - r, cy - r, cx + r, cy + r],
        fill=CIRCLE_COLOR
    )

    # Draw the show name inside the circle
    badge_font = get_font(SANS_FONT, 28)
    badge_bbox = draw.textbbox((0, 0), SHOW_BADGE, font=badge_font)
    badge_w = badge_bbox[2] - badge_bbox[0]
    badge_h = badge_bbox[3] - badge_bbox[1]
    draw.text(
        (cx - badge_w // 2, cy - badge_h // 2 - 12),
        SHOW_BADGE,
        fill=WHITE,
        font=badge_font
    )

    # Draw the smaller subtitle lines under it
    small_font = get_font(SANS_REGULAR, 8)
    for line_y, sub_text in zip((cy + 8, cy + 19), SHOW_SUBTITLE):
        sub_bbox = draw.textbbox((0, 0), sub_text, font=small_font)
        sub_w = sub_bbox[2] - sub_bbox[0]
        draw.text(
            (cx - sub_w // 2, line_y),
            sub_text,
            fill=WHITE,
            font=small_font
        )

    # --- "In Conversation With" text ---
    conv_font = get_font(SANS_REGULAR, 26)
    draw.text(CONV_TEXT_POS, "In Conversation With", fill=WHITE, font=conv_font)

    # --- Guest Name (large chalk-style text) ---
    name_lines = split_name_lines(name)
    name_font, name_size = auto_size_name_font(draw, name_lines)

    # Calculate total name block height and center it
    line_spacing = int(name_size * 1.25)
    total_name_height = len(name_lines) * line_spacing

    # Position name block
    name_y = NAME_START_Y
    for line in name_lines:
        draw.text((NAME_X, name_y), line, fill=WHITE, font=name_font)
        name_y += line_spacing

    # --- Wavy decorative line ---
    wavy_y = max(name_y + 20, WAVY_Y)
    draw_wavy_line(draw, DESIGNATION_X, DESIGNATION_X + 200, wavy_y, amplitude=3, wavelength=15, width=2)

    # --- Designation + Company ---
    desig_font = get_font(SANS_FONT, 22)
    designation_text = f"{designation.upper()} - {company.upper()}"
    draw.text((DESIGNATION_X, DESIGNATION_Y), designation_text, fill=WHITE, font=desig_font)

    # --- Place headshot ---
    if headshot_path and os.path.exists(headshot_path):
        headshot = Image.open(headshot_path).convert("RGBA")

        # Calculate scaling to fit the right side
        h_width, h_height = headshot.size

        # Scale to fill the right portion nicely
        # Target: person should fill most of the right side vertically
        scale_h = HEADSHOT_MAX_HEIGHT / h_height
        scale_w = HEADSHOT_MAX_WIDTH / h_width
        scale = min(scale_h, scale_w)

        # Allow slightly larger if person is small
        if scale * h_height < 500:
            scale = 500 / h_height

        new_w = int(h_width * scale)
        new_h = int(h_height * scale)
        headshot = headshot.resize((new_w, new_h), Image.LANCZOS)

        # Position: align bottom, push to right side
        paste_x = CANVAS_WIDTH - new_w + 20  # Slight overflow right is ok
        paste_x = max(paste_x, HEADSHOT_X_START)  # Don't go too far left
        paste_y = CANVAS_HEIGHT - new_h  # Align to bottom
        paste_y = max(paste_y, 30)  # Don't go above top

        # Paste with alpha mask for transparency
        img.paste(headshot, (paste_x, paste_y), headshot)

    # Save
    img = img.convert("RGB")
    img.save(output_path, "JPEG", quality=95)
    print(f"Thumbnail saved: {output_path}")
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a podcast YouTube thumbnail")
    parser.add_argument("--name", required=True, help="Guest's full name")
    parser.add_argument("--designation", required=True, help="Guest's title/designation")
    parser.add_argument("--company", required=True, help="Company name")
    parser.add_argument("--headshot", required=True, help="Path to headshot image (PNG with transparent bg)")
    parser.add_argument("--output", default="thumbnail-output.jpg", help="Output file path")

    args = parser.parse_args()
    generate_thumbnail(args.name, args.designation, args.company, args.headshot, args.output)
