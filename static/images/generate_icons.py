#!/usr/bin/env python3
"""
Simple icon generator for TopStyle PWA
Creates basic colored squares as placeholder icons
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size, filename):
    """Create a simple icon with TopStyle branding"""
    # Create a new image with a blue background
    img = Image.new('RGB', (size, size), color='#007bff')
    draw = ImageDraw.Draw(img)
    
    # Add a white circle in the center
    margin = size // 8
    draw.ellipse([margin, margin, size-margin, size-margin], fill='white')
    
    # Add "TS" text in the center
    try:
        # Try to use a system font
        font_size = size // 3
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Calculate text position
    text = "TS"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    # Draw the text
    draw.text((x, y), text, fill='#007bff', font=font)
    
    # Save the image
    img.save(filename, 'PNG')
    print(f"Created {filename} ({size}x{size})")

def main():
    """Generate all required icon sizes"""
    sizes = [72, 96, 128, 144, 152, 192, 384, 512]
    
    for size in sizes:
        filename = f"icon-{size}x{size}.png"
        create_icon(size, filename)
    
    # Create shortcut icons
    create_icon(96, "shortcut-order.png")
    create_icon(96, "shortcut-track.png") 
    create_icon(96, "shortcut-inventory.png")
    
    # Create screenshot placeholders
    create_screenshot(1280, 720, "screenshot-dashboard.png")
    create_screenshot(750, 1334, "screenshot-orders.png")

def create_screenshot(width, height, filename):
    """Create a placeholder screenshot"""
    img = Image.new('RGB', (width, height), color='#f8f9fa')
    draw = ImageDraw.Draw(img)
    
    # Add a simple mockup
    draw.rectangle([50, 50, width-50, height-50], outline='#007bff', width=2)
    draw.text((width//2-100, height//2), f"TopStyle {width}x{height}", fill='#007bff')
    
    img.save(filename, 'PNG')
    print(f"Created {filename} ({width}x{height})")

if __name__ == "__main__":
    main()
