#!/usr/bin/env python3
"""
Logo Extractor Script
Analyzes an image with multiple logos and extracts each one into separate PNG files.
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw
import os
import json
from pathlib import Path

class LogoExtractor:
    def __init__(self, image_path, output_dir="extracted_logos"):
        """
        Initialize the LogoExtractor
        
        Args:
            image_path (str): Path to the input image
            output_dir (str): Directory to save extracted logos
        """
        self.image_path = image_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Load image
        self.image = cv2.imread(image_path)
        self.pil_image = Image.open(image_path)
        self.height, self.width = self.image.shape[:2]
        
        # Logo detection parameters
        self.min_logo_area = 5000  # Minimum area for a logo
        self.max_logo_area = self.width * self.height * 0.3  # Max 30% of image
        self.padding = 20  # Padding around detected logos
        
    def detect_logos_contours(self):
        """
        Detect logos using contour detection method
        Returns list of bounding boxes (x, y, w, h)
        """
        # Convert to grayscale
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold to get binary image
        _, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
        
        # Morphological operations to clean up
        kernel = np.ones((3,3), np.uint8)
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        logo_boxes = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if self.min_logo_area < area < self.max_logo_area:
                x, y, w, h = cv2.boundingRect(contour)
                # Add padding
                x = max(0, x - self.padding)
                y = max(0, y - self.padding)
                w = min(self.width - x, w + 2 * self.padding)
                h = min(self.height - y, h + 2 * self.padding)
                logo_boxes.append((x, y, w, h))
        
        return logo_boxes
    
    def detect_logos_grid(self):
        """
        Detect logos assuming they're arranged in a rough grid
        Uses adaptive approach based on whitespace detection
        """
        # Convert to grayscale
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        
        # Create binary mask (non-white areas)
        mask = gray < 250
        
        # Find horizontal and vertical projections
        h_projection = np.sum(mask, axis=1)  # Sum across width
        v_projection = np.sum(mask, axis=0)  # Sum across height
        
        # Find row boundaries (areas with low horizontal projection)
        row_boundaries = self.find_boundaries(h_projection, min_gap=30)
        col_boundaries = self.find_boundaries(v_projection, min_gap=50)
        
        logo_boxes = []
        
        # For each row, find logos
        for i in range(len(row_boundaries) - 1):
            row_start = row_boundaries[i]
            row_end = row_boundaries[i + 1]
            
            # Get the row slice
            row_mask = mask[row_start:row_end, :]
            row_v_projection = np.sum(row_mask, axis=0)
            
            # Find logo boundaries in this row
            logo_boundaries = self.find_boundaries(row_v_projection, min_gap=30)
            
            for j in range(len(logo_boundaries) - 1):
                col_start = logo_boundaries[j] 
                col_end = logo_boundaries[j + 1]
                
                # Check if this region has significant content
                region_mask = mask[row_start:row_end, col_start:col_end]
                if np.sum(region_mask) > 1000:  # Minimum content threshold
                    # Add padding
                    x = max(0, col_start - self.padding)
                    y = max(0, row_start - self.padding)
                    w = min(self.width - x, col_end - col_start + 2 * self.padding)
                    h = min(self.height - y, row_end - row_start + 2 * self.padding)
                    
                    logo_boxes.append((x, y, w, h))
        
        return logo_boxes
    
    def find_boundaries(self, projection, min_gap=20):
        """
        Find boundaries in projection where gaps occur
        """
        boundaries = [0]
        in_gap = projection[0] < min_gap
        
        for i in range(1, len(projection)):
            current_low = projection[i] < min_gap
            
            if in_gap and not current_low:  # End of gap
                boundaries.append(i)
            elif not in_gap and current_low:  # Start of gap
                # Don't add boundary immediately, wait for gap to end
                pass
                
            in_gap = current_low
        
        boundaries.append(len(projection))
        return boundaries
    
    def manual_coordinates(self):
        """
        Manually defined coordinates for the logos in the specific image
        Based on visual inspection of the layout
        """
        # These coordinates are specific to this particular logo arrangement
        # Format: (x, y, width, height)
        coordinates = [
            # Row 1
            (45, 30, 290, 120),    # NM DOT
            (370, 30, 320, 120),   # Los Alamos
            (720, 30, 320, 120),   # Colorado Springs Utilities
            
            # Row 2  
            (45, 180, 240, 80),    # Wilson & Company
            (320, 180, 240, 80),   # RMF Engineering
            (680, 180, 280, 80),   # US Dept of Energy
            
            # Row 3
            (45, 290, 240, 120),   # Cross Connection Inc
            (320, 290, 240, 120),  # RED Rochester
            (580, 290, 100, 100),  # NASA
            (720, 290, 320, 120),  # Frank Lill & Son
            
            # Row 4
            (45, 440, 320, 120),   # MWH
            (400, 460, 280, 80),   # Stantec
            (400, 520, 280, 60),   # Futures Mechanical
            
            # Row 5
            (45, 580, 240, 120),   # SET INC
            (320, 670, 120, 80),   # UCLA
            (480, 580, 240, 120),  # Bechtel
            (760, 580, 180, 120),  # AECOM
            
            # Row 6 (Bottom)
            (45, 750, 180, 120),   # DLS Construction
            (240, 750, 240, 120),  # Twenty20 Construction
            (480, 750, 320, 120),  # Los Alamos (where discoveries are made)
            (820, 750, 180, 120),  # Pueblo Electric
            
            # Row 7
            (45, 900, 280, 80),    # Raytheon
        ]
        
        return coordinates
    
    def extract_logos(self, method="auto"):
        """
        Extract logos using specified method
        
        Args:
            method (str): "auto", "contours", "grid", or "manual"
        """
        print(f"Extracting logos using {method} method...")
        
        if method == "manual":
            logo_boxes = self.manual_coordinates()
        elif method == "contours":
            logo_boxes = self.detect_logos_contours()
        elif method == "grid":
            logo_boxes = self.detect_logos_grid()
        else:  # auto - try multiple methods
            logo_boxes = self.detect_logos_grid()
            if len(logo_boxes) < 10:  # If we didn't find enough logos
                print("Grid method found few logos, trying contours...")
                contour_boxes = self.detect_logos_contours()
                logo_boxes.extend(contour_boxes)
        
        print(f"Found {len(logo_boxes)} potential logos")
        
        # Extract and save each logo
        logo_info = []
        for i, (x, y, w, h) in enumerate(logo_boxes):
            try:
                # Extract logo region
                logo_region = self.pil_image.crop((x, y, x + w, y + h))
                
                # Generate filename
                filename = f"logo_{i+1:02d}.png"
                filepath = self.output_dir / filename
                
                # Save logo
                logo_region.save(filepath, "PNG")
                print(f"Saved: {filename} ({w}x{h} at {x},{y})")
                
                logo_info.append({
                    "filename": filename,
                    "coordinates": [x, y, w, h],
                    "size": [w, h]
                })
                
            except Exception as e:
                print(f"Error extracting logo {i+1}: {e}")
        
        # Save extraction info
        info_file = self.output_dir / "extraction_info.json"
        with open(info_file, 'w') as f:
            json.dump({
                "source_image": self.image_path,
                "method": method,
                "total_logos": len(logo_info),
                "logos": logo_info
            }, f, indent=2)
        
        return logo_info
    
    def create_preview(self, logo_boxes, output_file="detection_preview.png"):
        """
        Create a preview image showing detected logo boundaries
        """
        preview_image = self.pil_image.copy()
        draw = ImageDraw.Draw(preview_image)
        
        for i, (x, y, w, h) in enumerate(logo_boxes):
            # Draw rectangle
            draw.rectangle([(x, y), (x + w, y + h)], outline="red", width=3)
            # Add label
            draw.text((x, y - 20), f"Logo {i+1}", fill="red")
        
        preview_image.save(output_file)
        print(f"Preview saved: {output_file}")

def main():
    """
    Main function to run logo extraction
    """
    image_path = "client-logos-collection.png"
    
    if not os.path.exists(image_path):
        print(f"Error: Image file '{image_path}' not found!")
        return
    
    # Create extractor
    extractor = LogoExtractor(image_path)
    
    # Try manual method first (most accurate for this specific image)
    print("Attempting manual coordinate extraction...")
    logo_info = extractor.extract_logos(method="manual")
    
    if len(logo_info) < 10:
        print("Manual method found few logos, trying automatic detection...")
        logo_info = extractor.extract_logos(method="auto")
    
    print(f"\nExtraction complete! {len(logo_info)} logos saved to '{extractor.output_dir}'")
    
    # Create preview
    if logo_info:
        coordinates = [info["coordinates"] for info in logo_info]
        extractor.create_preview(coordinates)

if __name__ == "__main__":
    main()