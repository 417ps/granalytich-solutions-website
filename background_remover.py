#!/usr/bin/env python3
"""
Background Remover for Logos
Makes backgrounds transparent by removing white/light backgrounds
"""

import os
from PIL import Image
import numpy as np

def remove_background(image_path, output_path, threshold=240):
    """
    Remove white/light backgrounds from logos
    threshold: RGB values above this will be made transparent (default 240 = very light colors)
    """
    with Image.open(image_path) as img:
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Convert to numpy array
        data = np.array(img)
        
        # Get RGB channels
        rgb = data[:, :, :3]
        alpha = data[:, :, 3]
        
        # Find pixels that are close to white (light backgrounds)
        # A pixel is considered background if all RGB values are above threshold
        is_background = np.all(rgb >= threshold, axis=2)
        
        # Alternative method: also remove pixels that are very close to white
        # Calculate brightness for each pixel
        brightness = np.mean(rgb, axis=2)
        is_very_bright = brightness >= threshold
        
        # Combine both conditions
        background_mask = is_background | is_very_bright
        
        # Set alpha to 0 (transparent) for background pixels
        alpha[background_mask] = 0
        
        # Create new image data
        new_data = data.copy()
        new_data[:, :, 3] = alpha
        
        # Convert back to PIL Image and save
        transparent_img = Image.fromarray(new_data, 'RGBA')
        transparent_img.save(output_path, 'PNG')

def process_logos_for_transparency(input_dir, threshold=240):
    """Process all PNG files to remove backgrounds"""
    
    processed_count = 0
    
    # Process each PNG file in the main directory (not subfolders)
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.png') and not filename.endswith('-black.png') and not filename.endswith('-white.png'):
            input_path = os.path.join(input_dir, filename)
            
            # Skip if it's a directory
            if os.path.isdir(input_path):
                continue
                
            # Create output path (overwrite original)
            output_path = input_path
            
            try:
                remove_background(input_path, output_path, threshold)
                print(f"Processed: {filename}")
                processed_count += 1
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    
    return processed_count

if __name__ == "__main__":
    # Set paths
    input_directory = os.path.expanduser("~/Downloads/granalytic-logos")
    
    print("Removing backgrounds from colored logos...")
    print(f"Processing directory: {input_directory}")
    print("Threshold: 240 (pixels with RGB values >= 240 will be made transparent)")
    print()
    
    processed = process_logos_for_transparency(input_directory, threshold=240)
    
    print(f"\nBackground removal complete!")
    print(f"Processed {processed} logo files")
    print("Original files have been updated with transparent backgrounds")