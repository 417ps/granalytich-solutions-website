#!/usr/bin/env python3
"""
Blob Center Detection for Logo Extraction
Finds the center of each logo blob and automatically sizes extraction boxes
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageDraw
from sklearn.cluster import DBSCAN
from collections import defaultdict
import matplotlib.pyplot as plt

def detect_logo_centers(image_path, debug=True):
    """
    Detect centers of logo blobs using computer vision
    """
    # Load image
    image = cv2.imread(image_path)
    original = image.copy()
    
    # Convert to RGB for PIL compatibility
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(image_rgb)
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Create mask for non-white pixels (actual content)
    # White pixels have high values, content pixels have lower values
    _, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    
    # Clean up the binary image
    kernel = np.ones((3,3), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    
    # Find all contours (potential logo blobs)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours by area (remove tiny artifacts)
    min_area = 1000  # Minimum area for a logo
    max_area = 50000  # Maximum area for a logo
    
    valid_contours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if min_area < area < max_area:
            valid_contours.append(contour)
    
    print(f"Found {len(valid_contours)} potential logo blobs")
    
    # Calculate centers and bounding info for each valid contour
    logo_centers = []
    
    for i, contour in enumerate(valid_contours):
        # Calculate moments to find centroid
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])  # Center X
            cy = int(M["m01"] / M["m00"])  # Center Y
        else:
            # Fallback to bounding box center
            x, y, w, h = cv2.boundingRect(contour)
            cx = x + w // 2
            cy = y + h // 2
        
        # Get bounding rectangle
        x, y, w, h = cv2.boundingRect(contour)
        area = cv2.contourArea(contour)
        
        # Calculate aspect ratio and other features
        aspect_ratio = w / h if h > 0 else 1
        
        logo_info = {
            'id': i,
            'center': (cx, cy),
            'bbox': (x, y, w, h),
            'area': area,
            'aspect_ratio': aspect_ratio,
            'contour': contour
        }
        
        logo_centers.append(logo_info)
        
        print(f"Logo {i}: Center=({cx}, {cy}), BBox=({x}, {y}, {w}, {h}), Area={area:.0f}")
    
    # Sort by Y coordinate (top to bottom), then X coordinate (left to right)
    logo_centers.sort(key=lambda x: (x['center'][1] // 100, x['center'][0]))
    
    if debug:
        # Create debug visualization
        debug_image = original.copy()
        
        for i, logo in enumerate(logo_centers):
            cx, cy = logo['center']
            x, y, w, h = logo['bbox']
            
            # Draw contour
            cv2.drawContours(debug_image, [logo['contour']], -1, (0, 255, 0), 2)
            
            # Draw center point
            cv2.circle(debug_image, (cx, cy), 5, (255, 0, 0), -1)
            
            # Draw bounding box
            cv2.rectangle(debug_image, (x, y), (x + w, y + h), (255, 255, 0), 2)
            
            # Add label
            cv2.putText(debug_image, f'#{i}', (cx - 10, cy - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        
        # Save debug image
        debug_path = 'blob_detection_debug.png'
        cv2.imwrite(debug_path, debug_image)
        print(f"Debug visualization saved to: {debug_path}")
    
    return logo_centers, pil_image

def create_smart_extraction_boxes(logo_centers, padding=20):
    """
    Create extraction boxes around detected logo centers
    """
    extraction_coords = []
    
    for i, logo in enumerate(logo_centers):
        cx, cy = logo['center']
        bbox_x, bbox_y, bbox_w, bbox_h = logo['bbox']
        
        # Use bounding box as base, add padding
        x = max(0, bbox_x - padding)
        y = max(0, bbox_y - padding)
        width = bbox_w + (2 * padding)
        height = bbox_h + (2 * padding)
        
        # Create extraction coordinate
        coord = {
            'id': i,
            'name': f'detected-logo-{i:02d}',
            'center': (cx, cy),
            'x': x,
            'y': y,
            'width': width,
            'height': height,
            'area': logo['area'],
            'aspect_ratio': logo['aspect_ratio']
        }
        
        extraction_coords.append(coord)
        
        print(f"Logo {i:2d}: Center=({cx:3d}, {cy:3d}) -> Box=({x:3d}, {y:3d}, {width:3d}, {height:3d})")
    
    return extraction_coords

def create_extraction_preview(image, extraction_coords, output_file="blob_extraction_preview.html"):
    """
    Create HTML preview showing detected centers and extraction boxes
    """
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Blob Center Detection & Extraction Preview</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .container {{ position: relative; display: inline-block; }}
        .center-point {{ position: absolute; width: 10px; height: 10px; 
                        background: red; border-radius: 50%; 
                        transform: translate(-5px, -5px); z-index: 3; }}
        .extraction-box {{ position: absolute; border: 3px solid blue; 
                          background: rgba(0,0,255,0.1); z-index: 2; }}
        .label {{ position: absolute; background: white; padding: 2px 5px; 
                 font-size: 12px; font-weight: bold; z-index: 4; }}
        .info {{ margin: 20px 0; }}
        table {{ border-collapse: collapse; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>Blob Center Detection Results</h1>
    <div class="info">
        <p><strong>Red dots</strong> = Detected logo centers</p>
        <p><strong>Blue boxes</strong> = Proposed extraction areas</p>
        <p><strong>Labels</strong> = Logo ID numbers</p>
    </div>
    
    <div class="container">
        <img src="client-logos-collection-v2.png" alt="Logo Collection" style="max-width: 100%;">
"""
    
    # Add center points and extraction boxes
    for coord in extraction_coords:
        cx, cy = coord['center']
        x, y, width, height = coord['x'], coord['y'], coord['width'], coord['height']
        logo_id = coord['id']
        
        # Center point
        html_content += f'''
        <div class="center-point" style="left: {cx}px; top: {cy}px;"></div>
        '''
        
        # Extraction box
        html_content += f'''
        <div class="extraction-box" 
             style="left: {x}px; top: {y}px; width: {width}px; height: {height}px;">
        </div>
        '''
        
        # Label
        html_content += f'''
        <div class="label" style="left: {cx + 10}px; top: {cy - 10}px;">#{logo_id}</div>
        '''
    
    html_content += """
    </div>
    
    <table>
        <tr>
            <th>ID</th>
            <th>Center (x, y)</th>
            <th>Extraction Box (x, y, w, h)</th>
            <th>Area</th>
            <th>Aspect Ratio</th>
        </tr>
"""
    
    # Add table rows
    for coord in extraction_coords:
        cx, cy = coord['center']
        x, y, width, height = coord['x'], coord['y'], coord['width'], coord['height']
        
        html_content += f"""
        <tr>
            <td>#{coord['id']}</td>
            <td>({cx}, {cy})</td>
            <td>({x}, {y}, {width}, {height})</td>
            <td>{coord['area']:.0f}</td>
            <td>{coord['aspect_ratio']:.2f}</td>
        </tr>"""
    
    html_content += """
    </table>
</body>
</html>"""
    
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    return output_file

def main():
    """
    Main blob detection and extraction workflow
    """
    print("Blob Center Detection for Logo Extraction")
    print("=" * 50)
    
    image_path = "client-logos-collection-v2.png"
    
    if not os.path.exists(image_path):
        print(f"Error: Image file {image_path} not found!")
        return
    
    # Step 1: Detect logo centers
    print("\n1. Detecting logo centers...")
    logo_centers, pil_image = detect_logo_centers(image_path, debug=True)
    
    # Step 2: Create smart extraction boxes
    print(f"\n2. Creating extraction boxes for {len(logo_centers)} detected logos...")
    extraction_coords = create_smart_extraction_boxes(logo_centers, padding=15)
    
    # Step 3: Create preview
    print("\n3. Creating extraction preview...")
    html_file = create_extraction_preview(pil_image, extraction_coords)
    
    # Step 4: Extract logos
    print("\n4. Extracting logos...")
    output_dir = "blob-detected-logos"
    os.makedirs(output_dir, exist_ok=True)
    
    extracted_count = 0
    for coord in extraction_coords:
        x, y, width, height = coord['x'], coord['y'], coord['width'], coord['height']
        
        # Extract logo region
        logo_region = pil_image.crop((x, y, x + width, y + height))
        
        # Save extracted logo
        filename = f"{coord['name']}.png"
        output_path = os.path.join(output_dir, filename)
        logo_region.save(output_path, "PNG")
        extracted_count += 1
        
        print(f"  ✅ Extracted: {filename}")
    
    print(f"\n📊 Summary:")
    print(f"Detected logo blobs: {len(logo_centers)}")
    print(f"Extracted logos: {extracted_count}")
    print(f"Debug image: blob_detection_debug.png")
    print(f"Preview HTML: {html_file}")
    print(f"Extracted logos: {output_dir}/")
    
    return extraction_coords, html_file

if __name__ == "__main__":
    main()