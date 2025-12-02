#!/usr/bin/env python3
"""Create thumbnail versions of screenshot images."""

from pathlib import Path
from PIL import Image
import sys

ROOT = Path(__file__).resolve().parents[1]
IMAGES_DIR = ROOT / "docs" / "assets" / "images"

THUMBNAIL_SIZE = (300, 200)  # width, height
THUMBNAIL_QUALITY = 85

def create_thumbnail(source_path: Path, dest_path: Path) -> bool:
    """Create a thumbnail from source image."""
    try:
        with Image.open(source_path) as img:
            # Convert to RGB if necessary (for PNG with transparency)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create a white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Create thumbnail maintaining aspect ratio
            img.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
            
            # Save thumbnail
            img.save(dest_path, 'JPEG', quality=THUMBNAIL_QUALITY, optimize=True)
            print(f"Created thumbnail: {dest_path.name}")
            return True
    except Exception as e:
        print(f"Error creating thumbnail for {source_path.name}: {e}", file=sys.stderr)
        return False

def main():
    """Create thumbnails for all screenshot images."""
    if not IMAGES_DIR.exists():
        print(f"Images directory not found: {IMAGES_DIR}", file=sys.stderr)
        return 1
    
    screenshot_files = [
        "screenshot.png",
        "screenshot_2.png",
        "screenshot_3.png",
        "screenshot_4.png"
    ]
    
    success_count = 0
    total_count = 0
    
    for screenshot_file in screenshot_files:
        source_path = IMAGES_DIR / screenshot_file
        
        if not source_path.exists():
            print(f"Warning: {screenshot_file} not found, skipping", file=sys.stderr)
            continue
        
        # Create thumbnail filename
        base_name = screenshot_file.replace('.png', '')
        thumb_filename = f"{base_name}_thumb.png"
        dest_path = IMAGES_DIR / thumb_filename
        
        total_count += 1
        if create_thumbnail(source_path, dest_path):
            success_count += 1
    
    print(f"\nThumbnails created: {success_count}/{total_count}")
    return 0 if success_count == total_count else 1

if __name__ == "__main__":
    sys.exit(main())

