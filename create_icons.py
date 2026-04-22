#!/usr/bin/env python3
"""
GhostOffice Icon Generator
Creates professional PWA icons with ghost motif and amber branding
"""

from PIL import Image, ImageDraw, ImageFont
import math

def create_ghost_icon(size, output_path):
    """
    Create a GhostOffice icon with ghost motif and amber accent

    Args:
        size: Icon size (192 or 512)
        output_path: Output file path
    """
    # Create image with dark background
    img = Image.new('RGBA', (size, size), (10, 10, 11, 255))  # #0A0A0B
    draw = ImageDraw.Draw(img)

    # Calculate dimensions based on size
    center = size // 2
    ghost_scale = size // 3
    ghost_width = ghost_scale
    ghost_height = int(ghost_scale * 1.3)

    # Ghost body (rounded top, flat bottom with jagged edge)
    ghost_top = center - ghost_height // 2
    ghost_bottom = center + ghost_height // 2
    ghost_left = center - ghost_width // 2
    ghost_right = center + ghost_width // 2

    # Draw ghost body with gradient effect
    # Main body
    ghost_color = (245, 158, 11, 255)  # #F59E0B amber

    # Create ghost shape
    points = [
        # Top curve
        (ghost_left, ghost_top + ghost_height // 3),
        (ghost_left + ghost_width // 4, ghost_top),
        (center, ghost_top - ghost_height // 6),
        (ghost_right - ghost_width // 4, ghost_top),
        (ghost_right, ghost_top + ghost_height // 3),
        # Right side
        (ghost_right, ghost_bottom - ghost_height // 4),
        # Jagged bottom
        (ghost_right - ghost_width // 5, ghost_bottom),
        (ghost_right - ghost_width // 2.5, ghost_bottom - ghost_height // 5),
        (ghost_right - ghost_width // 2, ghost_bottom),
        (ghost_right - ghost_width // 1.7, ghost_bottom - ghost_height // 5),
        (ghost_right - ghost_width // 1.25, ghost_bottom),
        (ghost_left + ghost_width // 5, ghost_bottom),
        (ghost_left + ghost_width // 2.5, ghost_bottom - ghost_height // 5),
        (ghost_left + ghost_width // 2, ghost_bottom),
        (ghost_left + ghost_width // 1.7, ghost_bottom - ghost_height // 5),
        (ghost_left + ghost_width // 1.25, ghost_bottom),
        # Left side
        (ghost_left, ghost_bottom - ghost_height // 4),
    ]

    # Draw ghost with glow effect
    # Outer glow
    glow_radius = size // 10
    for i in range(glow_radius, 0, -2):
        alpha = int(30 * (1 - i / glow_radius))
        glow_color = (245, 158, 11, alpha)
        glow_points = [(x + i//2, y + i//2) for x, y in points]
        draw.polygon(glow_points, fill=glow_color)

    # Main ghost body
    draw.polygon(points, fill=ghost_color)

    # Ghost eyes
    eye_radius = size // 25
    eye_y = ghost_top + ghost_height // 3
    left_eye_x = center - ghost_width // 4
    right_eye_x = center + ghost_width // 4

    # Eye whites
    draw.ellipse([
        left_eye_x - eye_radius, eye_y - eye_radius,
        left_eye_x + eye_radius, eye_y + eye_radius
    ], fill=(10, 10, 11, 255))

    draw.ellipse([
        right_eye_x - eye_radius, eye_y - eye_radius,
        right_eye_x + eye_radius, eye_y + eye_radius
    ], fill=(10, 10, 11, 255))

    # Eye pupils (amber)
    pupil_radius = eye_radius // 2
    draw.ellipse([
        left_eye_x - pupil_radius, eye_y - pupil_radius,
        left_eye_x + pupil_radius, eye_y + pupil_radius
    ], fill=(245, 158, 11, 255))

    draw.ellipse([
        right_eye_x - pupil_radius, eye_y - pupil_radius,
        right_eye_x + pupil_radius, eye_y + pupil_radius
    ], fill=(245, 158, 11, 255))

    # Add subtle amber glow around the icon
    glow_overlay = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_overlay)

    # Create radial gradient glow
    for r in range(size // 2, 0, -4):
        alpha = int(20 * (1 - r / (size // 2)))
        glow_draw.ellipse([
            center - r, center - r,
            center + r, center + r
        ], fill=(245, 158, 11, alpha))

    # Composite glow
    img = Image.alpha_composite(img, glow_overlay)

    # Save the image
    img.save(output_path, 'PNG')
    print(f"✅ Created {output_path} ({size}x{size})")

def main():
    """Create all required icons"""
    print("🎨 Creating GhostOffice icons...")

    # Create icons directory if it doesn't exist
    import os
    public_dir = "/media/matrix/DATA/opencode_projects/officeghost/ui-upgrade/public"
    os.makedirs(public_dir, exist_ok=True)

    # Create 192x192 icon
    create_ghost_icon(192, f"{public_dir}/icon-192.png")

    # Create 512x512 icon
    create_ghost_icon(512, f"{public_dir}/icon-512.png")

    print("✨ All icons created successfully!")

if __name__ == "__main__":
    main()