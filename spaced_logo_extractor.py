#!/usr/bin/env python3
"""
Spaced Logo Extractor
Extracts logos from the new spaced-out layout with validation
"""

import os
from PIL import Image, ImageDraw
import numpy as np
from sklearn.cluster import KMeans
from collections import Counter
import cv2

def analyze_color_scheme(image_region, n_colors=5):
    """Analyze color scheme to detect inconsistencies"""
    img_array = np.array(image_region)
    
    if len(img_array.shape) != 3 or img_array.shape[2] != 3:
        if image_region.mode != 'RGB':
            image_region = image_region.convert('RGB')
            img_array = np.array(image_region)
    
    pixels = img_array.reshape(-1, 3)
    non_white_mask = np.sum(pixels, axis=1) < 720
    non_white_pixels = pixels[non_white_mask]
    
    if len(non_white_pixels) == 0:
        return [], []
    
    n_clusters = min(n_colors, len(non_white_pixels))
    if n_clusters < 2:
        return [], []
        
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans.fit(non_white_pixels)
    
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
    """Detect color inconsistencies suggesting encroachment"""
    colors, percentages = analyze_color_scheme(image_region, n_colors=8)
    
    if len(colors) < 2:
        return False
    
    hsv_colors = []
    for color in colors:
        rgb_normalized = np.array(color).reshape(1, 1, 3).astype(np.uint8)
        hsv = cv2.cvtColor(rgb_normalized, cv2.COLOR_RGB2HSV)[0, 0]
        hsv_colors.append(hsv)
    
    hues = [hsv[0] for hsv in hsv_colors]
    
    hue_clusters = KMeans(n_clusters=min(3, len(hues)), random_state=42, n_init=10)
    hue_clusters.fit(np.array(hues).reshape(-1, 1))
    
    hue_centers = hue_clusters.cluster_centers_.flatten()
    
    if len(hue_centers) >= 2:
        max_hue_diff = max(hue_centers) - min(hue_centers)
        if max_hue_diff > 90:
            max_hue_diff = min(max_hue_diff, 180 - max_hue_diff)
        
        if max_hue_diff > 60:
            return True
    
    return False

def validate_logo_boundaries(image, x, y, width, height, company_name):
    """Validate logo boundaries using multiple methods"""
    region = image.crop((x, y, x + width, y + height))
    
    has_inconsistencies = detect_color_inconsistencies(region)
    
    region_array = np.array(region.convert('L'))
    edges = cv2.Canny(region_array, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    border_threshold = 10
    h, w = region_array.shape
    
    top_border = np.mean(region_array[:border_threshold, :]) < 240
    bottom_border = np.mean(region_array[-border_threshold:, :]) < 240
    left_border = np.mean(region_array[:, :border_threshold]) < 240
    right_border = np.mean(region_array[:, -border_threshold:]) < 240
    
    border_content = sum([top_border, bottom_border, left_border, right_border])
    
    validation_results = {
        'company': company_name,
        'coordinates': (x, y, width, height),
        'color_inconsistencies': has_inconsistencies,
        'border_content_count': border_content,
        'needs_adjustment': has_inconsistencies or border_content > 2,
        'contour_count': len(contours)
    }
    
    return validation_results

def create_html_preview(image, logo_coords, validation_results, output_file="spaced_logo_validation.html"):
    """Create HTML preview with validation results"""
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Spaced Logo Extraction Validation</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .container {{ position: relative; display: inline-block; }}
        .logo-box {{ position: absolute; border: 3px solid; cursor: pointer; }}
        .valid {{ border-color: green; background: rgba(0,255,0,0.15); }}
        .invalid {{ border-color: red; background: rgba(255,0,0,0.15); }}
        .warning {{ border-color: orange; background: rgba(255,165,0,0.15); }}
        .info {{ margin: 20px 0; }}
        .legend {{ margin: 10px 0; }}
        .legend span {{ display: inline-block; width: 20px; height: 20px; margin-right: 5px; }}
        table {{ border-collapse: collapse; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .needs-adjustment {{ background-color: #ffebee; }}
    </style>
</head>
<body>
    <h1>Spaced Logo Extraction Validation Results</h1>
    <div class="info">
        <div class="legend">
            <span style="background-color: rgba(0,255,0,0.3); border: 3px solid green;"></span> Valid extraction
            <span style="background-color: rgba(255,165,0,0.3); border: 3px solid orange;"></span> Needs review
            <span style="background-color: rgba(255,0,0,0.3); border: 3px solid red;"></span> Likely encroachment
        </div>
    </div>
    
    <div class="container">
        <img src="client-logos-collection-v2.png" alt="Spaced Logo Collection" style="max-width: 100%;">
"""
    
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

def extract_spaced_logos():
    """Extract logos from the new spaced layout"""
    
    image_path = "client-logos-collection-v2.png"
    image = Image.open(image_path)
    
    # New coordinates based on spaced layout
    logo_coords = [
        # Row 1 - Top row with good spacing
        {"name": "nm-dot", "x": 40, "y": 30, "width": 270, "height": 130},
        {"name": "los-alamos-national-lab", "x": 330, "y": 45, "width": 360, "height": 100},
        {"name": "colorado-springs-utilities", "x": 710, "y": 30, "width": 320, "height": 130},
        
        # Row 2 - Second row
        {"name": "wilson-company", "x": 40, "y": 200, "width": 230, "height": 90},
        {"name": "rmf-engineering", "x": 280, "y": 220, "width": 410, "height": 80},
        {"name": "us-doe", "x": 710, "y": 200, "width": 320, "height": 90},
        
        # Row 3 - Third row
        {"name": "cross-connection-inc", "x": 40, "y": 340, "width": 240, "height": 120},
        {"name": "red-rochester", "x": 300, "y": 340, "width": 280, "height": 120},
        {"name": "nasa", "x": 600, "y": 340, "width": 120, "height": 120},
        
        # Row 4 - Fourth row  
        {"name": "frank-lill-son", "x": 40, "y": 480, "width": 340, "height": 100},
        {"name": "stantec", "x": 400, "y": 480, "width": 300, "height": 100},
        {"name": "futures-mechanical", "x": 720, "y": 500, "width": 320, "height": 80},
        
        # Row 5 - Fifth row
        {"name": "mwh-global", "x": 40, "y": 620, "width": 340, "height": 120},
        {"name": "set-inc", "x": 400, "y": 620, "width": 300, "height": 120},
        {"name": "ucla", "x": 720, "y": 660, "width": 160, "height": 80},
        
        # Row 6 - Sixth row
        {"name": "bechtel", "x": 40, "y": 810, "width": 200, "height": 120},
        {"name": "aecom", "x": 280, "y": 830, "width": 280, "height": 80},
        {"name": "dls-construction", "x": 580, "y": 810, "width": 200, "height": 120},
        {"name": "twenty20-construction", "x": 800, "y": 810, "width": 240, "height": 120},
        
        # Row 7 - Bottom row
        {"name": "los-alamos-research", "x": 40, "y": 1000, "width": 340, "height": 80},
        {"name": "pueblo-electric", "x": 400, "y": 1000, "width": 300, "height": 80},
        {"name": "raytheon", "x": 720, "y": 1000, "width": 320, "height": 80},
    ]
    
    print("Validating spaced logo extractions...")
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
    
    # Extract all logos (both valid and invalid for comparison)
    output_dir = "spaced-logos"
    os.makedirs(output_dir, exist_ok=True)
    
    extracted_count = 0
    for coord, validation in zip(logo_coords, validation_results):
        logo_region = image.crop((coord['x'], coord['y'], 
                                coord['x'] + coord['width'], 
                                coord['y'] + coord['height']))
        
        filename = f"logo-{coord['name']}.png"
        output_path = os.path.join(output_dir, filename)
        logo_region.save(output_path, "PNG")
        extracted_count += 1
        
        status_icon = "✅" if not validation['needs_adjustment'] else "⚠️"
        print(f"{status_icon} Extracted: {filename}")
    
    print(f"\n📊 Summary:")
    print(f"Total logos extracted: {extracted_count}")
    valid_count = sum(1 for v in validation_results if not v['needs_adjustment'])
    print(f"Valid extractions: {valid_count}")
    print(f"Need adjustment: {extracted_count - valid_count}")
    print(f"\nValidation report: {html_file}")
    
    return validation_results, html_file

if __name__ == "__main__":
    print("Spaced Logo Extraction with Validation")
    print("=" * 50)
    validation_results, html_file = extract_spaced_logos()
    print(f"\nOpen {html_file} in a browser to review extraction validation!")