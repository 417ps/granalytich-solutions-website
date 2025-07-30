#!/usr/bin/env python3
"""
Refined Logo Extractor
Extracts individual logos with careful boundary detection to avoid cutting off content
"""

import os
from PIL import Image, ImageDraw
import numpy as np

def analyze_logo_boundaries(image, x, y, width, height, padding=10):
    """
    Analyze the boundaries of a logo area to ensure we're not cutting off content
    Returns refined coordinates with proper white borders
    """
    # Convert to numpy array for analysis
    img_array = np.array(image)
    
    # Define the region to analyze (with some padding)
    x1 = max(0, x - padding)
    y1 = max(0, y - padding)
    x2 = min(image.width, x + width + padding)
    y2 = min(image.height, y + height + padding)
    
    # Extract the region
    region = img_array[y1:y2, x1:x2]
    
    # Find the actual content boundaries by looking for non-white pixels
    # Define white as RGB values > 245 (to account for slight variations)
    if len(region.shape) == 3:  # RGB image
        is_white = np.all(region >= 245, axis=2)
    else:  # Grayscale
        is_white = region >= 245
    
    # Find non-white pixels (actual logo content)
    content_mask = ~is_white
    
    # Find the bounding box of actual content
    content_rows = np.any(content_mask, axis=1)
    content_cols = np.any(content_mask, axis=0)
    
    if not np.any(content_rows) or not np.any(content_cols):
        # No content found, return original coordinates
        return x, y, width, height
    
    # Find the actual content boundaries
    content_top = np.where(content_rows)[0][0]
    content_bottom = np.where(content_rows)[0][-1]
    content_left = np.where(content_cols)[0][0]
    content_right = np.where(content_cols)[0][-1]
    
    # Convert back to absolute coordinates
    abs_content_left = x1 + content_left
    abs_content_top = y1 + content_top
    abs_content_right = x1 + content_right
    abs_content_bottom = y1 + content_bottom
    
    # Add padding around the actual content
    margin = 15  # White margin around content
    final_x = max(0, abs_content_left - margin)
    final_y = max(0, abs_content_top - margin)
    final_width = min(image.width - final_x, abs_content_right - abs_content_left + 2 * margin)
    final_height = min(image.height - final_y, abs_content_bottom - abs_content_top + 2 * margin)
    
    return final_x, final_y, final_width, final_height

def extract_refined_logos():
    """Extract logos with refined boundary detection"""
    
    # Load the image
    image_path = "client-logos-collection.png"
    image = Image.open(image_path)
    
    # Initial logo coordinates (approximate positions)
    logo_coords = [
        # Row 1
        {"name": "nm-dot", "x": 0, "y": 0, "width": 350, "height": 180},
        {"name": "los-alamos-national-lab", "x": 350, "y": 0, "width": 400, "height": 180},
        {"name": "colorado-springs-utilities", "x": 750, "y": 0, "width": 350, "height": 180},
        
        # Row 2  
        {"name": "wilson-company", "x": 0, "y": 180, "width": 280, "height": 140},
        {"name": "rmf-engineering", "x": 280, "y": 180, "width": 400, "height": 140},
        {"name": "us-doe", "x": 680, "y": 180, "width": 420, "height": 140},
        
        # Row 3
        {"name": "cross-connection-inc", "x": 0, "y": 320, "width": 280, "height": 140},
        {"name": "red-rochester", "x": 280, "y": 320, "width": 280, "height": 140},
        {"name": "nasa", "x": 560, "y": 320, "width": 140, "height": 140},
        {"name": "frank-lill-son", "x": 700, "y": 320, "width": 400, "height": 140},
        
        # Row 4
        {"name": "stantec", "x": 0, "y": 460, "width": 380, "height": 120},
        {"name": "futures-mechanical", "x": 380, "y": 460, "width": 320, "height": 120},
        {"name": "mwh-global", "x": 700, "y": 460, "width": 400, "height": 120},
        
        # Row 5
        {"name": "set-inc", "x": 0, "y": 580, "width": 300, "height": 160},
        {"name": "ucla", "x": 300, "y": 580, "width": 200, "height": 160},
        {"name": "bechtel", "x": 500, "y": 580, "width": 250, "height": 160},
        {"name": "aecom", "x": 750, "y": 580, "width": 350, "height": 160},
        
        # Row 6
        {"name": "dls-construction", "x": 0, "y": 740, "width": 230, "height": 140},
        {"name": "twenty20-construction", "x": 230, "y": 740, "width": 250, "height": 140},
        {"name": "los-alamos-research", "x": 480, "y": 740, "width": 420, "height": 140},
        {"name": "pueblo-electric", "x": 900, "y": 740, "width": 200, "height": 140},
        
        # Row 7
        {"name": "raytheon", "x": 0, "y": 880, "width": 400, "height": 120},
    ]
    
    # Create output directory
    output_dir = "refined-logos"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a preview image to show extraction areas
    preview_img = image.copy()
    draw = ImageDraw.Draw(preview_img)
    
    extracted_logos = []
    
    for i, coord in enumerate(logo_coords, 1):
        print(f"Processing logo {i}: {coord['name']}")
        
        # Analyze and refine boundaries
        refined_x, refined_y, refined_width, refined_height = analyze_logo_boundaries(
            image, coord['x'], coord['y'], coord['width'], coord['height']
        )
        
        # Draw rectangle on preview (original in red, refined in green)
        draw.rectangle([coord['x'], coord['y'], coord['x'] + coord['width'], coord['y'] + coord['height']], 
                      outline="red", width=2)
        draw.rectangle([refined_x, refined_y, refined_x + refined_width, refined_y + refined_height], 
                      outline="green", width=2)
        
        # Extract the refined logo
        logo_region = image.crop((refined_x, refined_y, refined_x + refined_width, refined_y + refined_height))
        
        # Save the logo
        filename = f"logo-{coord['name']}.png"
        output_path = os.path.join(output_dir, filename)
        logo_region.save(output_path, "PNG")
        
        extracted_logos.append({
            "filename": filename,
            "company": coord['name'].replace('-', ' ').title(),
            "original_coords": (coord['x'], coord['y'], coord['width'], coord['height']),
            "refined_coords": (refined_x, refined_y, refined_width, refined_height)
        })
        
        print(f"  Original: ({coord['x']}, {coord['y']}, {coord['width']}, {coord['height']})")
        print(f"  Refined:  ({refined_x}, {refined_y}, {refined_width}, {refined_height})")
        print(f"  Saved: {filename}")
    
    # Save preview image
    preview_img.save("refined_extraction_preview.png", "PNG")
    print(f"\nExtraction complete!")
    print(f"Preview saved as: refined_extraction_preview.png")
    print(f"Red rectangles = Original coordinates")
    print(f"Green rectangles = Refined coordinates")
    print(f"Logos saved to: {output_dir}/")
    
    return extracted_logos

if __name__ == "__main__":
    print("Refined Logo Extraction with Boundary Analysis")
    print("=" * 50)
    extracted = extract_refined_logos()
    print(f"\nSuccessfully extracted {len(extracted)} logos with refined boundaries!")