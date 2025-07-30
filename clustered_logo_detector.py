#!/usr/bin/env python3
"""
Clustered Logo Detection
Groups nearby blob centers that belong to the same logo using distance clustering
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageDraw
from sklearn.cluster import DBSCAN
from collections import defaultdict
import matplotlib.pyplot as plt

def detect_logo_blobs(image_path, min_area=500, max_area=100000):
    """
    Detect all individual blobs in the image
    """
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Create binary mask for non-white pixels
    _, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    
    # Clean up noise
    kernel = np.ones((2,2), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
    
    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Extract blob information
    blobs = []
    for i, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if min_area < area < max_area:
            # Calculate center
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
            else:
                x, y, w, h = cv2.boundingRect(contour)
                cx = x + w // 2
                cy = y + h // 2
            
            # Get bounding info
            x, y, w, h = cv2.boundingRect(contour)
            
            blob = {
                'id': i,
                'center': (cx, cy),
                'bbox': (x, y, w, h),
                'area': area,
                'contour': contour
            }
            blobs.append(blob)
    
    print(f"Found {len(blobs)} individual blobs")
    return blobs, image

def check_connectivity_between_blobs(image, blob1, blob2, threshold=240):
    """
    Check if there are significant colored pixels between two blob centers
    Returns True if blobs should be merged
    """
    cx1, cy1 = blob1['center']
    cx2, cy2 = blob2['center']
    
    # Create a line between the two centers and sample pixels along it
    distance = np.sqrt((cx2 - cx1)**2 + (cy2 - cy1)**2)
    
    if distance > 200:  # Don't check very distant blobs
        return False
    
    # Sample points along the line between centers
    num_samples = int(distance / 5)  # Sample every 5 pixels
    if num_samples < 2:
        return True  # Very close blobs should be merged
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    colored_pixels = 0
    
    for i in range(num_samples):
        t = i / (num_samples - 1)
        x = int(cx1 + t * (cx2 - cx1))
        y = int(cy1 + t * (cy2 - cy1))
        
        if 0 <= x < gray.shape[1] and 0 <= y < gray.shape[0]:
            pixel_value = gray[y, x]
            if pixel_value < threshold:  # Non-white pixel
                colored_pixels += 1
    
    # If more than 30% of sampled pixels are colored, merge the blobs
    connectivity_ratio = colored_pixels / num_samples
    return connectivity_ratio > 0.3

def cluster_logo_centers(blobs, min_distance=120, image=None):
    """
    Cluster nearby blob centers that belong to the same logo
    min_distance: minimum pixels between separate logos
    image: original image for connectivity analysis
    """
    if len(blobs) == 0:
        return []
    
    # Extract center coordinates
    centers = np.array([blob['center'] for blob in blobs])
    
    # Use DBSCAN clustering with minimum distance parameter
    # eps = minimum distance between points in same cluster (reduced to capture close text)
    # min_samples = minimum points to form a cluster (set to 1 to allow single-blob logos)
    clustering = DBSCAN(eps=min_distance * 0.8, min_samples=1).fit(centers)
    
    # Group blobs by cluster
    clusters = defaultdict(list)
    for i, label in enumerate(clustering.labels_):
        clusters[label].append(blobs[i])
    
    # Post-process: merge clusters that have connectivity between them
    if image is not None:
        merged_any = True
        while merged_any:
            merged_any = False
            cluster_list = list(clusters.items())
            
            for i, (cluster_id1, blobs1) in enumerate(cluster_list):
                if cluster_id1 not in clusters:  # Already merged
                    continue
                    
                for j, (cluster_id2, blobs2) in enumerate(cluster_list[i+1:], i+1):
                    if cluster_id2 not in clusters:  # Already merged
                        continue
                    
                    # Check if any blob from cluster1 connects to any blob from cluster2
                    should_merge = False
                    for blob1 in blobs1:
                        for blob2 in blobs2:
                            if check_connectivity_between_blobs(image, blob1, blob2):
                                should_merge = True
                                break
                        if should_merge:
                            break
                    
                    if should_merge:
                        # Merge cluster2 into cluster1
                        clusters[cluster_id1].extend(clusters[cluster_id2])
                        del clusters[cluster_id2]
                        merged_any = True
                        print(f"  Merged clusters {cluster_id1} and {cluster_id2} due to connectivity")
                        break
    
    print(f"Clustered {len(blobs)} blobs into {len(clusters)} logo groups")
    
    # Create combined logo information for each cluster
    clustered_logos = []
    for cluster_id, cluster_blobs in clusters.items():
        # Calculate combined bounding box for all blobs in cluster
        all_x = []
        all_y = []
        total_area = 0
        
        for blob in cluster_blobs:
            x, y, w, h = blob['bbox']
            all_x.extend([x, x + w])
            all_y.extend([y, y + h])
            total_area += blob['area']
        
        # Combined bounding box
        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)
        combined_width = max_x - min_x
        combined_height = max_y - min_y
        
        # Calculate center of combined logo
        combined_cx = min_x + combined_width // 2
        combined_cy = min_y + combined_height // 2
        
        logo_info = {
            'cluster_id': cluster_id,
            'center': (combined_cx, combined_cy),
            'bbox': (min_x, min_y, combined_width, combined_height),
            'total_area': total_area,
            'blob_count': len(cluster_blobs),
            'individual_blobs': cluster_blobs
        }
        
        clustered_logos.append(logo_info)
        
        print(f"Logo {cluster_id}: Center=({combined_cx}, {combined_cy}), "
              f"BBox=({min_x}, {min_y}, {combined_width}, {combined_height}), "
              f"Blobs={len(cluster_blobs)}, Area={total_area:.0f}")
    
    # Sort by position (top to bottom, left to right)
    clustered_logos.sort(key=lambda x: (x['center'][1] // 150, x['center'][0]))
    
    return clustered_logos

def create_extraction_boxes(clustered_logos, padding=25):
    """
    Create extraction boxes around clustered logo groups
    """
    extraction_coords = []
    
    for i, logo in enumerate(clustered_logos):
        cx, cy = logo['center']
        bbox_x, bbox_y, bbox_w, bbox_h = logo['bbox']
        
        # Add padding around the combined bounding box
        x = max(0, bbox_x - padding)
        y = max(0, bbox_y - padding)
        width = bbox_w + (2 * padding)
        height = bbox_h + (2 * padding)
        
        coord = {
            'id': i,
            'name': f'clustered-logo-{i:02d}',
            'center': (cx, cy),
            'x': x,
            'y': y,
            'width': width,
            'height': height,
            'total_area': logo['total_area'],
            'blob_count': logo['blob_count'],
            'cluster_id': logo['cluster_id']
        }
        
        extraction_coords.append(coord)
        
        print(f"Logo {i:2d}: Center=({cx:3d}, {cy:3d}) -> Box=({x:3d}, {y:3d}, {width:3d}, {height:3d}) "
              f"[{logo['blob_count']} blobs]")
    
    return extraction_coords

def create_debug_visualization(image, blobs, clustered_logos, output_file="clustered_debug.png"):
    """
    Create debug image showing individual blobs and clustered results
    """
    debug_image = image.copy()
    
    # Colors for different clusters
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), 
              (0, 255, 255), (128, 128, 128), (255, 128, 0), (128, 255, 0), (128, 0, 255)]
    
    # Draw individual blobs in light colors
    for blob in blobs:
        cv2.drawContours(debug_image, [blob['contour']], -1, (200, 200, 200), 1)
        cx, cy = blob['center']
        cv2.circle(debug_image, (cx, cy), 3, (128, 128, 128), -1)
    
    # Draw clustered logos
    for i, logo in enumerate(clustered_logos):
        color = colors[i % len(colors)]
        
        # Draw combined bounding box
        x, y, w, h = logo['bbox']
        cv2.rectangle(debug_image, (x, y), (x + w, y + h), color, 3)
        
        # Draw center of combined logo
        cx, cy = logo['center']
        cv2.circle(debug_image, (cx, cy), 8, color, -1)
        cv2.circle(debug_image, (cx, cy), 8, (255, 255, 255), 2)
        
        # Add label
        cv2.putText(debug_image, f'#{i}', (cx - 15, cy - 15), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
        # Highlight individual blobs in this cluster
        for blob in logo['individual_blobs']:
            cv2.drawContours(debug_image, [blob['contour']], -1, color, 2)
    
    cv2.imwrite(output_file, debug_image)
    print(f"Debug visualization saved to: {output_file}")
    return output_file

def create_extraction_preview(image, extraction_coords, output_file="clustered_extraction_preview.html"):
    """
    Create HTML preview of clustered extraction results
    """
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(image_rgb)
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Clustered Logo Extraction Preview</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .container {{ position: relative; display: inline-block; }}
        .center-point {{ position: absolute; width: 16px; height: 16px; 
                        background: red; border: 3px solid white; border-radius: 50%; 
                        transform: translate(-8px, -8px); z-index: 3; }}
        .extraction-box {{ position: absolute; border: 4px solid blue; 
                          background: rgba(0,0,255,0.1); z-index: 2; }}
        .label {{ position: absolute; background: white; padding: 3px 8px; 
                 font-size: 14px; font-weight: bold; border: 2px solid blue;
                 z-index: 4; }}
        .info {{ margin: 20px 0; }}
        .legend {{ margin: 10px 0; font-size: 16px; }}
        .legend span {{ display: inline-block; width: 20px; height: 20px; margin-right: 8px; }}
        table {{ border-collapse: collapse; margin-top: 20px; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .multi-blob {{ background-color: #e8f5e8; }}
    </style>
</head>
<body>
    <h1>Clustered Logo Detection Results</h1>
    <div class="info">
        <div class="legend">
            <p><span style="background: red; border: 3px solid white; border-radius: 50%;"></span> 
               <strong>Red dots</strong> = Clustered logo centers</p>
            <p><span style="background: rgba(0,0,255,0.3); border: 4px solid blue;"></span> 
               <strong>Blue boxes</strong> = Extraction areas (with padding)</p>
            <p><strong>Labels</strong> = Final logo ID numbers</p>
        </div>
        <p><strong>Clustering Parameters:</strong> Minimum distance between logos = 120 pixels</p>
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
        <div class="label" style="left: {cx + 15}px; top: {cy - 15}px;">#{logo_id}</div>
        '''
    
    html_content += """
    </div>
    
    <table>
        <tr>
            <th>ID</th>
            <th>Center (x, y)</th>
            <th>Extraction Box (x, y, w, h)</th>
            <th>Total Area</th>
            <th>Blob Count</th>
            <th>Type</th>
        </tr>
"""
    
    # Add table rows
    for coord in extraction_coords:
        cx, cy = coord['center']
        x, y, width, height = coord['x'], coord['y'], coord['width'], coord['height']
        
        row_class = "multi-blob" if coord['blob_count'] > 1 else ""
        logo_type = f"Multi-part ({coord['blob_count']} blobs)" if coord['blob_count'] > 1 else "Single blob"
        
        html_content += f"""
        <tr class="{row_class}">
            <td>#{coord['id']}</td>
            <td>({cx}, {cy})</td>
            <td>({x}, {y}, {width}, {height})</td>
            <td>{coord['total_area']:.0f}</td>
            <td>{coord['blob_count']}</td>
            <td>{logo_type}</td>
        </tr>"""
    
    html_content += """
    </table>
    
    <div style="margin-top: 20px;">
        <p><strong>Green rows</strong> = Logos composed of multiple parts (text + graphics)</p>
        <p><strong>White rows</strong> = Simple single-blob logos</p>
    </div>
</body>
</html>"""
    
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    return output_file

def main():
    """
    Main clustered logo detection workflow
    """
    print("Clustered Logo Detection")
    print("=" * 50)
    
    image_path = "client-logos-collection-v2.png"
    
    if not os.path.exists(image_path):
        print(f"Error: Image file {image_path} not found!")
        return
    
    # Step 1: Detect individual blobs
    print("\n1. Detecting individual blobs...")
    blobs, image = detect_logo_blobs(image_path)
    
    # Step 2: Cluster nearby blobs into logos
    print(f"\n2. Clustering blobs into logos (min distance = 120px)...")
    clustered_logos = cluster_logo_centers(blobs, min_distance=120, image=image)
    
    # Step 3: Create extraction boxes
    print(f"\n3. Creating extraction boxes for {len(clustered_logos)} clustered logos...")
    extraction_coords = create_extraction_boxes(clustered_logos)
    
    # Step 4: Create visualizations
    print("\n4. Creating visualizations...")
    debug_file = create_debug_visualization(image, blobs, clustered_logos)
    html_file = create_extraction_preview(image, extraction_coords)
    
    # Step 5: Extract logos
    print("\n5. Extracting clustered logos...")
    output_dir = "clustered-logos"
    os.makedirs(output_dir, exist_ok=True)
    
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(image_rgb)
    
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
        
        blob_info = f"({coord['blob_count']} blobs)" if coord['blob_count'] > 1 else ""
        print(f"  ✅ Extracted: {filename} {blob_info}")
    
    print(f"\n📊 Summary:")
    print(f"Individual blobs detected: {len(blobs)}")
    print(f"Clustered into logos: {len(clustered_logos)}")
    print(f"Extracted logo files: {extracted_count}")
    print(f"Debug visualization: {debug_file}")
    print(f"HTML preview: {html_file}")
    print(f"Extracted logos: {output_dir}/")
    
    return extraction_coords, html_file

if __name__ == "__main__":
    main()