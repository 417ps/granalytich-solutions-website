#!/usr/bin/env python3
"""
Logo Color Converter
Converts logos to black and white versions while preserving transparency
"""

import os
from PIL import Image
import numpy as np

def convert_to_black(image_path, output_path):
    """Convert logo to black version - converts all non-transparent pixels to black"""
    with Image.open(image_path) as img:
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Convert to numpy array
        data = np.array(img)
        
        # Get alpha channel (transparency)
        alpha = data[:, :, 3]
        
        # Create black version - set RGB to black where alpha > 0
        black_data = data.copy()
        mask = alpha > 0  # Non-transparent pixels
        black_data[mask, 0] = 0  # Red = 0
        black_data[mask, 1] = 0  # Green = 0  
        black_data[mask, 2] = 0  # Blue = 0
        # Keep original alpha channel
        
        # Convert back to PIL Image and save
        black_img = Image.fromarray(black_data, 'RGBA')
        black_img.save(output_path, 'PNG')

def convert_to_white(image_path, output_path):
    """Convert logo to white version - converts all non-transparent pixels to white"""
    with Image.open(image_path) as img:
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Convert to numpy array
        data = np.array(img)
        
        # Get alpha channel (transparency)
        alpha = data[:, :, 3]
        
        # Create white version - set RGB to white where alpha > 0
        white_data = data.copy()
        mask = alpha > 0  # Non-transparent pixels
        white_data[mask, 0] = 255  # Red = 255
        white_data[mask, 1] = 255  # Green = 255
        white_data[mask, 2] = 255  # Blue = 255
        # Keep original alpha channel
        
        # Convert back to PIL Image and save
        white_img = Image.fromarray(white_data, 'RGBA')
        white_img.save(output_path, 'PNG')

def process_logos(input_dir, output_dir):
    """Process all PNG files in input directory"""
    
    # Create output directories
    black_dir = os.path.join(output_dir, 'black-versions')
    white_dir = os.path.join(output_dir, 'white-versions')
    os.makedirs(black_dir, exist_ok=True)
    os.makedirs(white_dir, exist_ok=True)
    
    # Process each PNG file
    for filename in os.listdir(input_dir):
        if filename.lower().endswith('.png'):
            input_path = os.path.join(input_dir, filename)
            
            # Create black version
            black_filename = filename.replace('.png', '-black.png')
            black_output = os.path.join(black_dir, black_filename)
            convert_to_black(input_path, black_output)
            print(f"Created black version: {black_filename}")
            
            # Create white version  
            white_filename = filename.replace('.png', '-white.png')
            white_output = os.path.join(white_dir, white_filename)
            convert_to_white(input_path, white_output)
            print(f"Created white version: {white_filename}")

if __name__ == "__main__":
    # Set paths
    input_directory = os.path.expanduser("~/Downloads/granalytic-logos")
    output_directory = os.path.expanduser("~/Downloads/granalytic-logos")
    
    print("Converting logos to black and white versions...")
    print(f"Input directory: {input_directory}")
    print(f"Output directory: {output_directory}")
    
    process_logos(input_directory, output_directory)
    print("\nConversion complete!")
    print("Black versions saved to: ~/Downloads/granalytic-logos/black-versions/")
    print("White versions saved to: ~/Downloads/granalytic-logos/white-versions/")