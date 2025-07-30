#!/usr/bin/env python3
"""
Improved Logo Extractor Script with Better Coordinates
Re-extracts logos with proper boundaries to avoid cutoffs
"""

import cv2
import numpy as np
from PIL import Image
import os
from pathlib import Path

class ImprovedLogoExtractor:
    def __init__(self, image_path, output_dir="logos"):
        """
        Initialize the ImprovedLogoExtractor
        
        Args:
            image_path (str): Path to the input image
            output_dir (str): Directory to save extracted logos
        """
        self.image_path = image_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Load image
        self.pil_image = Image.open(image_path)
        self.width, self.height = self.pil_image.size
        
    def get_improved_coordinates(self):
        """
        Improved coordinates based on visual inspection of the original image
        Format: (x, y, width, height) with better boundaries
        """
        coordinates = [
            # Row 1 - Top row logos
            (30, 15, 350, 150),    # NM DOT - Full logo with tagline
            (360, 15, 370, 150),   # Los Alamos - Complete text
            (710, 15, 370, 150),   # Colorado Springs Utilities - Full tagline
            
            # Row 2 - Second row
            (30, 170, 280, 100),   # Wilson & Company - Complete underline
            (300, 170, 280, 100),  # RMF Engineering - Full text
            (660, 170, 320, 100),  # US Dept of Energy - Complete seal and text
            
            # Row 3 - Third row  
            (30, 280, 280, 140),   # Cross Connection Inc - Full tagline
            (290, 280, 280, 140),  # RED Rochester - Complete logo
            (560, 280, 130, 130),  # NASA - Full circular logo
            (710, 280, 370, 140),  # Frank Lill & Son - Complete text
            
            # Row 4 - Fourth row (Stantec and MWH area)
            (30, 450, 380, 140),   # Stantec - Full logo
            (380, 440, 320, 90),   # Futures Mechanical - upper part  
            (380, 520, 320, 70),   # Futures Mechanical - lower part
            (700, 430, 380, 150),  # MWH - Complete logo and tagline
            
            # Row 5 - Fifth row
            (30, 580, 280, 140),   # SET INC - Full logo with tagline
            (300, 660, 150, 100),  # UCLA - Complete logo
            (480, 580, 280, 180),  # Bechtel - Full logo
            (780, 580, 200, 140),  # AECOM - Complete text
            
            # Row 6 - Sixth row (bottom logos)
            (30, 740, 200, 140),   # DLS Construction
            (240, 740, 280, 140),  # Twenty20 Construction
            (460, 740, 380, 140),  # Los Alamos "where discoveries are made"
            (800, 740, 200, 140),  # Pueblo Electric
            
            # Row 7 - Bottom
            (30, 900, 320, 100),   # Raytheon - Complete text
        ]
        
        return coordinates
    
    def extract_improved_logos(self):
        """
        Extract logos using improved coordinates
        """
        coordinates = self.get_improved_coordinates()
        
        print(f"Extracting {len(coordinates)} logos with improved boundaries...")
        
        logo_info = []
        for i, (x, y, w, h) in enumerate(coordinates):
            try:
                # Extract logo region
                logo_region = self.pil_image.crop((x, y, x + w, y + h))
                
                # Generate filename
                filename = f"logo_{i+1:02d}.png"
                filepath = self.output_dir / filename
                
                # Save logo
                logo_region.save(filepath, "PNG")
                print(f"Improved: {filename} ({w}x{h} at {x},{y})")
                
                logo_info.append({
                    "filename": filename,
                    "coordinates": [x, y, w, h],
                    "size": [w, h]
                })
                
            except Exception as e:
                print(f"Error extracting logo {i+1}: {e}")
        
        return logo_info

def main():
    """
    Main function to run improved logo extraction
    """
    image_path = "client-logos-collection.png"
    
    if not os.path.exists(image_path):
        print(f"Error: Image file '{image_path}' not found!")
        return
    
    # Create improved extractor
    extractor = ImprovedLogoExtractor(image_path)
    
    # Extract with improved coordinates
    print("Extracting logos with improved boundaries...")
    logo_info = extractor.extract_improved_logos()
    
    print(f"\nImproved extraction complete! {len(logo_info)} logos saved to '{extractor.output_dir}'")

if __name__ == "__main__":
    main()