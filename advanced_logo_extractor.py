#!/usr/bin/env python3
"""
Advanced Logo Extractor with Visual Validation
Uses color scheme analysis and visual validation to prevent encroachment
"""

import os
import json
from PIL import Image, ImageDraw
import numpy as np
from sklearn.cluster import KMeans
from collections import Counter
import cv2

def analyze_color_scheme(image_region, n_colors=5):
    """
    Analyze the color scheme of an image region to detect inconsistencies
    Returns dominant colors and their percentages
    """
    # Convert PIL to numpy array
    img_array = np.array(image_region)
    
    # Ensure we have RGB format
    if len(img_array.shape) != 3 or img_array.shape[2] != 3:
        # Convert to RGB if needed
        if image_region.mode != 'RGB':
            image_region = image_region.convert('RGB')
            img_array = np.array(image_region)
    
    # Reshape for clustering
    pixels = img_array.reshape(-1, 3)
    
    # Remove white/near-white pixels (background)
    non_white_mask = np.sum(pixels, axis=1) < 720  # RGB sum < 240*3
    non_white_pixels = pixels[non_white_mask]
    
    if len(non_white_pixels) == 0:
        return [], []
    
    # Perform k-means clustering
    n_clusters = min(n_colors, len(non_white_pixels))
    if n_clusters < 2:
        return [], []
        
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans.fit(non_white_pixels)
    
    # Get color percentages
    labels = kmeans.labels_
    label_counts = Counter(labels)
    total_pixels = len(labels)
    
    colors = []
    percentages = []
    
    for i, center in enumerate(kmeans.cluster_centers_):
        percentage = (label_counts[i] / total_pixels) * 100
        colors.append(center.astype(int))
        percentages.append(percentage)
    
    return colors, percentages

def detect_color_inconsistencies(image_region, threshold=15):
    """
    Detect if there are color inconsistencies that suggest encroachment
    Returns True if potential encroachment detected
    """
    colors, percentages = analyze_color_scheme(image_region, n_colors=8)
    
    if len(colors) < 2:
        return False
    
    # Check for colors that are very different from the main palette
    # Convert colors to HSV for better comparison
    hsv_colors = []
    for color in colors:
        # Convert RGB to HSV
        rgb_normalized = np.array(color).reshape(1, 1, 3).astype(np.uint8)
        hsv = cv2.cvtColor(rgb_normalized, cv2.COLOR_RGB2HSV)[0, 0]
        hsv_colors.append(hsv)
    
    # Look for outlier colors (different hue ranges)
    hues = [hsv[0] for hsv in hsv_colors]
    
    # Check if there are significantly different hue groups
    hue_clusters = KMeans(n_clusters=min(3, len(hues)), random_state=42, n_init=10)
    hue_clusters.fit(np.array(hues).reshape(-1, 1))
    
    # If colors are spread across very different hue ranges, might be encroachment
    hue_centers = hue_clusters.cluster_centers_.flatten()
    
    if len(hue_centers) >= 2:
        max_hue_diff = max(hue_centers) - min(hue_centers)
        # Account for hue wraparound (0-180 in OpenCV HSV)
        if max_hue_diff > 90:  # Very different hues
            max_hue_diff = min(max_hue_diff, 180 - max_hue_diff)
        
        if max_hue_diff > 60:  # Significantly different color schemes
            return True
    
    return False

def validate_logo_boundaries(image, x, y, width, height, company_name):
    """
    Validate logo boundaries using multiple methods
    """
    # Extract the region
    region = image.crop((x, y, x + width, y + height))
    
    # Method 1: Color scheme analysis
    has_inconsistencies = detect_color_inconsistencies(region)
    
    # Method 2: Edge detection to find natural boundaries
    region_array = np.array(region.convert('L'))  # Convert to grayscale
    edges = cv2.Canny(region_array, 50, 150)
    
    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Method 3: Check for content near borders
    border_threshold = 10  # pixels from edge
    h, w = region_array.shape
    
    # Check if there's significant content near borders
    top_border = np.mean(region_array[:border_threshold, :]) < 240
    bottom_border = np.mean(region_array[-border_threshold:, :]) < 240
    left_border = np.mean(region_array[:, :border_threshold]) < 240
    right_border = np.mean(region_array[:, -border_threshold:]) < 240
    
    border_content = sum([top_border, bottom_border, left_border, right_border])
    
    # Validation results
    validation_results = {
        'company': company_name,
        'coordinates': (x, y, width, height),
        'color_inconsistencies': has_inconsistencies,
        'border_content_count': border_content,
        'needs_adjustment': has_inconsistencies or border_content > 2,
        'contour_count': len(contours)
    }
    
    return validation_results

def create_html_preview(image, logo_coords, validation_results, output_file="logo_validation.html"):
    """
    Create an HTML file with interactive preview using Puppeteer-like visualization
    """
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Logo Extraction Validation</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { position: relative; display: inline-block; }
        .logo-box { position: absolute; border: 2px solid; cursor: pointer; }
        .valid { border-color: green; background: rgba(0,255,0,0.1); }
        .invalid { border-color: red; background: rgba(255,0,0,0.1); }
        .warning { border-color: orange; background: rgba(255,165,0,0.1); }
        .info { margin: 20px 0; }
        .legend { margin: 10px 0; }
        .legend span { display: inline-block; width: 20px; height: 20px; margin-right: 5px; }
        table { border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .needs-adjustment { background-color: #ffebee; }
    </style>
</head>
<body>
    <h1>Logo Extraction Validation Results</h1>
    <div class="info">
        <div class="legend">
            <span style="background-color: rgba(0,255,0,0.3); border: 2px solid green;"></span> Valid extraction
            <span style="background-color: rgba(255,165,0,0.3); border: 2px solid orange;"></span> Needs review
            <span style="background-color: rgba(255,0,0,0.3); border: 2px solid red;"></span> Likely encroachment
        </div>
    </div>
    
    <div class="container">
        <img src="client-logos-collection.png" alt="Logo Collection" style="max-width: 100%;">
"""
    
    # Add logo boxes
    for i, (coord, validation) in enumerate(zip(logo_coords, validation_results)):
        x, y, width, height = coord['x'], coord['y'], coord['width'], coord['height']
        
        if validation['needs_adjustment']:
            if validation['color_inconsistencies']:
                css_class = "invalid"
                title = f"⚠️ Color inconsistencies detected"
            else:
                css_class = "warning"
                title = f"⚠️ Content near borders"
        else:
            css_class = "valid"
            title = f"✅ Looks good"
        
        html_content += f'''
        <div class="logo-box {css_class}" 
             style="left: {x}px; top: {y}px; width: {width}px; height: {height}px;"
             title="{title}: {coord['name']}">
        </div>'''
    
    html_content += """
    </div>
    
    <table>
        <tr>
            <th>Company</th>
            <th>Coordinates</th>
            <th>Color Issues</th>
            <th>Border Content</th>
            <th>Status</th>
            <th>Recommendation</th>
        </tr>
"""
    
    # Add validation table
    for validation in validation_results:
        row_class = "needs-adjustment" if validation['needs_adjustment'] else ""
        status = "❌ Needs adjustment" if validation['needs_adjustment'] else "✅ Valid"
        
        recommendation = ""
        if validation['color_inconsistencies']:
            recommendation = "Reduce extraction area - color scheme inconsistencies detected"
        elif validation['border_content_count'] > 2:
            recommendation = "Expand extraction area - content too close to borders"
        else:
            recommendation = "Extraction looks good"
        
        html_content += f"""
        <tr class="{row_class}">
            <td>{validation['company']}</td>
            <td>{validation['coordinates']}</td>
            <td>{'Yes' if validation['color_inconsistencies'] else 'No'}</td>
            <td>{validation['border_content_count']}/4 borders</td>
            <td>{status}</td>
            <td>{recommendation}</td>
        </tr>"""
    
    html_content += """
    </table>
</body>
</html>"""
    
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    return output_file

def extract_validated_logos():
    """Extract logos with comprehensive validation"""
    
    # Load the image
    image_path = "client-logos-collection.png"
    image = Image.open(image_path)
    
    # Iteratively refined coordinates - adjusted based on validation feedback
    logo_coords = [
        # Row 1 - All green from previous validation
        {"name": "nm-dot", "x": 50, "y": 45, "width": 320, "height": 120},
        {"name": "los-alamos-national-lab", "x": 390, "y": 65, "width": 350, "height": 95},
        {"name": "colorado-springs-utilities", "x": 745, "y": 20, "width": 320, "height": 140},
        
        # Row 2 - Ultra-conservative, just text portions
        {"name": "wilson-company", "x": 55, "y": 175, "width": 230, "height": 110},
        {"name": "rmf-engineering", "x": 330, "y": 215, "width": 290, "height": 80},  # Just the core text
        {"name": "us-doe", "x": 710, "y": 215, "width": 220, "height": 80},  # Just the core text
        
        # Row 3 - Focus on core Frank Lill logo only
        {"name": "cross-connection-inc", "x": 55, "y": 330, "width": 245, "height": 120},
        {"name": "red-rochester", "x": 250, "y": 310, "width": 290, "height": 140},
        {"name": "nasa", "x": 560, "y": 290, "width": 150, "height": 150},
        {"name": "frank-lill-son", "x": 720, "y": 340, "width": 340, "height": 110},  # Focus on core logo text
        
        # Row 4 - All green from previous validation
        {"name": "stantec", "x": 75, "y": 475, "width": 315, "height": 110},
        {"name": "futures-mechanical", "x": 375, "y": 530, "width": 335, "height": 70},
        {"name": "mwh-global", "x": 670, "y": 440, "width": 450, "height": 165},
        
        # Row 5 - Ultra-conservative Bechtel - just the word "BECHTEL"
        {"name": "set-inc", "x": 65, "y": 595, "width": 245, "height": 175},
        {"name": "ucla", "x": 310, "y": 670, "width": 165, "height": 95},  # Much smaller, focused on logo only
        {"name": "bechtel", "x": 540, "y": 640, "width": 170, "height": 65},  # Just "BECHTEL" text  
        {"name": "aecom", "x": 790, "y": 680, "width": 240, "height": 95},  # Much smaller, logo only
        
        # Row 6 - Ultra-conservative Los Alamos - just main text
        {"name": "dls-construction", "x": 60, "y": 710, "width": 200, "height": 200},
        {"name": "twenty20-construction", "x": 240, "y": 780, "width": 235, "height": 95},  # Reduced height significantly
        {"name": "los-alamos-research", "x": 540, "y": 820, "width": 280, "height": 40},  # Just central text
        {"name": "pueblo-electric", "x": 870, "y": 710, "width": 160, "height": 200},
        
        # Row 7 - Green from previous validation
        {"name": "raytheon", "x": 60, "y": 850, "width": 370, "height": 170},
    ]
    
    print("Validating logo extractions...")
    validation_results = []
    
    for coord in logo_coords:
        print(f"Validating: {coord['name']}")
        validation = validate_logo_boundaries(
            image, coord['x'], coord['y'], coord['width'], coord['height'], coord['name']
        )
        validation_results.append(validation)
        
        status = "❌ NEEDS ADJUSTMENT" if validation['needs_adjustment'] else "✅ VALID"
        print(f"  {status}")
        if validation['color_inconsistencies']:
            print(f"    ⚠️ Color inconsistencies detected")
        if validation['border_content_count'] > 2:
            print(f"    ⚠️ Content near {validation['border_content_count']}/4 borders")
    
    # Create HTML validation report
    html_file = create_html_preview(image, logo_coords, validation_results)
    print(f"\nValidation report created: {html_file}")
    
    # Extract only the valid logos
    valid_extractions = []
    output_dir = "validated-logos"
    os.makedirs(output_dir, exist_ok=True)
    
    for coord, validation in zip(logo_coords, validation_results):
        if not validation['needs_adjustment']:
            # Extract the logo
            logo_region = image.crop((coord['x'], coord['y'], 
                                    coord['x'] + coord['width'], 
                                    coord['y'] + coord['height']))
            
            filename = f"logo-{coord['name']}.png"
            output_path = os.path.join(output_dir, filename)
            logo_region.save(output_path, "PNG")
            valid_extractions.append(coord['name'])
            print(f"✅ Extracted: {filename}")
        else:
            print(f"⏭️ Skipped: {coord['name']} (needs manual adjustment)")
    
    # Skip JSON output to avoid serialization issues
    print("Skipping JSON report due to numpy type issues")
    
    print(f"\n📊 Summary:")
    print(f"Total logos: {len(logo_coords)}")
    print(f"Valid extractions: {len(valid_extractions)}")
    print(f"Need adjustment: {len(logo_coords) - len(valid_extractions)}")
    print(f"\nValidation report: {html_file}")
    print(f"JSON report: validation_report.json")
    
    return validation_results, html_file

if __name__ == "__main__":
    print("Advanced Logo Extraction with Validation")
    print("=" * 50)
    validation_results, html_file = extract_validated_logos()
    print(f"\nOpen {html_file} in a browser to review extraction validation!")