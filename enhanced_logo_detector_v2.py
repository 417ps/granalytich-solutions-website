#!/usr/bin/env python3
"""
Enhanced Logo Detector V2
Specifically designed for the cleaner client-logos-collection-v2.png layout
Uses advanced computer vision techniques for precise logo boundary detection
"""

import os
import json
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
from collections import defaultdict

class EnhancedLogoDetectorV2:
    def __init__(self, image_path="client-logos-collection-v2.png"):
        self.image_path = image_path
        self.image = Image.open(image_path)
        self.image_cv = cv2.imread(image_path)
        self.image_rgb = cv2.cvtColor(self.image_cv, cv2.COLOR_BGR2RGB)
        self.gray = cv2.cvtColor(self.image_cv, cv2.COLOR_BGR2GRAY)
        
        # Known company names for the V2 layout (based on visual inspection)
        self.expected_companies = [
            "New Mexico Department of Transportation",
            "Los Alamos National Laboratory", 
            "Colorado Springs Utilities",
            "Wilson & Company",
            "RMF Engineering",
            "U.S. Department of Energy",
            "Cross Connection Inc.",
            "RED Rochester LLC",
            "NASA",
            "Frank Lill & Son Inc.",
            "Stantec",
            "Futures Mechanical",
            "MWH Global",
            "SET Inc.",
            "UCLA",
            "Bechtel Corporation",
            "AECOM",
            "DLS Construction",
            "Twenty20 Construction",
            "Los Alamos National Laboratory",  # Second instance
            "Pueblo Electric Inc.",
            "Raytheon Company"
        ]

    def detect_content_regions(self):
        """
        Use advanced computer vision to detect actual content regions
        """
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(self.gray, (5, 5), 0)
        
        # Use adaptive thresholding to handle varying lighting
        binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY_INV, 11, 2)
        
        # Apply morphological operations to connect text elements
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 8))
        connected = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(connected, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by area and aspect ratio
        valid_contours = []
        min_area = 2000  # Minimum area for a logo
        max_area = 50000  # Maximum area to avoid noise
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if min_area < area < max_area:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter by aspect ratio (logos shouldn't be too tall and thin)
                aspect_ratio = w / h
                if 0.3 < aspect_ratio < 8.0:  # Reasonable aspect ratios
                    valid_contours.append(contour)
        
        return valid_contours

    def refine_bounding_boxes(self, contours):
        """
        Refine bounding boxes using content-aware analysis
        """
        refined_boxes = []
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Extract the region
            region = self.gray[y:y+h, x:x+w]
            
            # Find the actual content bounds within this region
            content_coords = np.where(region < 240)  # Non-white pixels
            
            if len(content_coords[0]) > 0:
                # Get tight bounds around actual content
                min_row, max_row = content_coords[0].min(), content_coords[0].max()
                min_col, max_col = content_coords[1].min(), content_coords[1].max()
                
                # Add padding
                padding = 10
                final_x = max(0, x + min_col - padding)
                final_y = max(0, y + min_row - padding)
                final_w = min(self.image.width - final_x, max_col - min_col + 2*padding)
                final_h = min(self.image.height - final_y, max_row - min_row + 2*padding)
                
                refined_boxes.append({
                    'x': final_x,
                    'y': final_y,
                    'width': final_w,
                    'height': final_h,
                    'area': final_w * final_h
                })
        
        return refined_boxes

    def cluster_logos_by_rows(self, boxes):
        """
        Group logos into rows using DBSCAN clustering
        """
        if not boxes:
            return []
        
        # Extract y-coordinates (vertical positions)
        y_coords = np.array([[box['y'] + box['height']/2] for box in boxes])
        
        # Use DBSCAN to cluster by rows
        clustering = DBSCAN(eps=50, min_samples=1).fit(y_coords)
        
        # Group boxes by cluster (row)
        rows = defaultdict(list)
        for i, label in enumerate(clustering.labels_):
            rows[label].append(boxes[i])
        
        # Sort rows by average y-coordinate
        sorted_rows = []
        for row_boxes in rows.values():
            avg_y = sum(box['y'] for box in row_boxes) / len(row_boxes)
            # Sort boxes within row by x-coordinate
            row_boxes.sort(key=lambda x: x['x'])
            sorted_rows.append((avg_y, row_boxes))
        
        sorted_rows.sort(key=lambda x: x[0])
        return [row_boxes for _, row_boxes in sorted_rows]

    def assign_company_names(self, logo_rows):
        """
        Assign company names based on expected layout
        """
        assigned_logos = []
        company_index = 0
        
        for row in logo_rows:
            for box in row:
                if company_index < len(self.expected_companies):
                    company_name = self.expected_companies[company_index]
                    
                    # Generate filename and short name
                    short_name = company_name.lower().replace(' ', '-').replace('&', 'and').replace('.', '').replace(',', '')
                    filename = f"logo_{company_index+1:02d}.png"
                    
                    assigned_logos.append({
                        'filename': filename,
                        'company': company_name,
                        'short_name': short_name,
                        'coordinates': box,
                        'alt': f"{company_name} Logo"
                    })
                    
                    company_index += 1
        
        return assigned_logos

    def validate_extractions(self, logos):
        """
        Validate logo extractions using multiple criteria
        """
        validated_logos = []
        
        for logo in logos:
            coords = logo['coordinates']
            x, y, w, h = coords['x'], coords['y'], coords['width'], coords['height']
            
            # Extract region for analysis
            region = self.image.crop((x, y, x + w, y + h))
            region_array = np.array(region.convert('L'))
            
            # Calculate validation metrics
            validation = {
                'has_content': np.mean(region_array < 240) > 0.05,  # At least 5% non-white
                'good_size': 1000 < (w * h) < 40000,  # Reasonable size
                'good_aspect': 0.5 < (w/h) < 6.0,  # Reasonable aspect ratio
                'content_density': np.mean(region_array < 240),
                'edge_content': self._check_edge_content(region_array)
            }
            
            # Score the extraction
            score = 0
            if validation['has_content']: score += 30
            if validation['good_size']: score += 25
            if validation['good_aspect']: score += 25
            if validation['content_density'] > 0.1: score += 10
            if not validation['edge_content']: score += 10
            
            logo['validation'] = validation
            logo['score'] = score
            logo['is_valid'] = score >= 70
            
            validated_logos.append(logo)
        
        return validated_logos

    def _check_edge_content(self, image_array, border_size=5):
        """
        Check if there's significant content near the edges
        """
        h, w = image_array.shape
        
        # Check each edge
        top_edge = np.mean(image_array[:border_size, :]) < 240
        bottom_edge = np.mean(image_array[-border_size:, :]) < 240
        left_edge = np.mean(image_array[:, :border_size]) < 240
        right_edge = np.mean(image_array[:, -border_size:]) < 240
        
        return any([top_edge, bottom_edge, left_edge, right_edge])

    def create_visual_preview(self, logos, output_path="enhanced_detection_preview_v2.html"):
        """
        Create an interactive HTML preview of detections
        """
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Enhanced Logo Detection V2 - Preview</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .container {{ position: relative; display: inline-block; margin-bottom: 20px; }}
        .logo-box {{ position: absolute; border: 3px solid; cursor: pointer; }}
        .valid {{ border-color: #4CAF50; background: rgba(76, 175, 80, 0.1); }}
        .invalid {{ border-color: #f44336; background: rgba(244, 67, 54, 0.1); }}
        .warning {{ border-color: #ff9800; background: rgba(255, 152, 0, 0.1); }}
        .info {{ margin: 20px 0; }}
        .legend {{ margin: 10px 0; }}
        .legend span {{ display: inline-block; width: 20px; height: 20px; margin-right: 5px; }}
        table {{ border-collapse: collapse; margin-top: 20px; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .score-high {{ background-color: #e8f5e8; }}
        .score-medium {{ background-color: #fff3cd; }}
        .score-low {{ background-color: #f8d7da; }}
        .tooltip {{ position: relative; display: inline-block; }}
        .tooltip .tooltiptext {{
            visibility: hidden;
            width: 300px;
            background-color: #333;
            color: #fff;
            text-align: left;
            border-radius: 6px;
            padding: 10px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -150px;
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 12px;
            line-height: 1.4;
        }}
        .tooltip:hover .tooltiptext {{
            visibility: visible;
            opacity: 1;
        }}
    </style>
</head>
<body>
    <h1>Enhanced Logo Detection V2 Results</h1>
    <div class="info">
        <p><strong>Image:</strong> {self.image_path}</p>
        <p><strong>Total Detections:</strong> {len(logos)}</p>
        <p><strong>Valid Extractions:</strong> {len([l for l in logos if l['is_valid']])}</p>
        <div class="legend">
            <span style="background-color: rgba(76, 175, 80, 0.3); border: 3px solid #4CAF50;"></span> Valid (Score ≥ 70)
            <span style="background-color: rgba(255, 152, 0, 0.3); border: 3px solid #ff9800;"></span> Needs Review (Score 50-69)
            <span style="background-color: rgba(244, 67, 54, 0.3); border: 3px solid #f44336;"></span> Invalid (Score < 50)
        </div>
    </div>
    
    <div class="container">
        <img src="{self.image_path}" alt="Logo Collection" style="max-width: 100%;">
"""
        
        # Add detection boxes
        for i, logo in enumerate(logos):
            coords = logo['coordinates']
            x, y, w, h = coords['x'], coords['y'], coords['width'], coords['height']
            score = logo['score']
            
            if score >= 70:
                css_class = "valid"
                status = "✅ Valid"
            elif score >= 50:
                css_class = "warning"
                status = "⚠️ Review"
            else:
                css_class = "invalid"
                status = "❌ Invalid"
            
            validation = logo['validation']
            tooltip_info = f"""
Company: {logo['company']}
Score: {score}/100
Size: {w}x{h} px
Content Density: {validation['content_density']:.1%}
Has Content: {'✅' if validation['has_content'] else '❌'}
Good Size: {'✅' if validation['good_size'] else '❌'}
Good Aspect: {'✅' if validation['good_aspect'] else '❌'}
Edge Content: {'⚠️' if validation['edge_content'] else '✅'}
            """.strip()
            
            html_content += f'''
        <div class="logo-box {css_class} tooltip" 
             style="left: {x}px; top: {y}px; width: {w}px; height: {h}px;">
            <span class="tooltiptext">{tooltip_info}</span>
        </div>'''
        
        html_content += """
    </div>
    
    <table>
        <tr>
            <th>Company</th>
            <th>Filename</th>
            <th>Coordinates</th>
            <th>Score</th>
            <th>Status</th>
            <th>Issues</th>
        </tr>
"""
        
        # Add results table
        for logo in logos:
            coords = logo['coordinates']
            score = logo['score']
            
            if score >= 70:
                row_class = "score-high"
            elif score >= 50:
                row_class = "score-medium"
            else:
                row_class = "score-low"
            
            status = "✅ Valid" if logo['is_valid'] else "❌ Invalid"
            
            issues = []
            val = logo['validation']
            if not val['has_content']: issues.append("No content")
            if not val['good_size']: issues.append("Bad size")
            if not val['good_aspect']: issues.append("Bad aspect")
            if val['edge_content']: issues.append("Edge content")
            
            issues_str = ", ".join(issues) if issues else "None"
            
            html_content += f"""
        <tr class="{row_class}">
            <td>{logo['company']}</td>
            <td>{logo['filename']}</td>
            <td>{coords['x']}, {coords['y']} ({coords['width']}×{coords['height']})</td>
            <td>{score}/100</td>
            <td>{status}</td>
            <td>{issues_str}</td>
        </tr>"""
        
        html_content += """
    </table>
    
    <script>
        // Add click functionality to logo boxes
        document.querySelectorAll('.logo-box').forEach(box => {
            box.addEventListener('click', function() {
                const rect = this.getBoundingClientRect();
                const tooltip = this.querySelector('.tooltiptext').textContent;
                alert(tooltip);
            });
        });
    </script>
</body>
</html>"""
        
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        return output_path

    def extract_valid_logos(self, logos, output_dir="enhanced-logos-v2"):
        """
        Extract only the valid logos to files
        """
        os.makedirs(output_dir, exist_ok=True)
        extracted_count = 0
        
        for logo in logos:
            if logo['is_valid']:
                coords = logo['coordinates']
                x, y, w, h = coords['x'], coords['y'], coords['width'], coords['height']
                
                # Extract the logo region
                logo_region = self.image.crop((x, y, x + w, y + h))
                
                # Save the logo
                output_path = os.path.join(output_dir, logo['filename'])
                logo_region.save(output_path, "PNG")
                extracted_count += 1
                
                print(f"✅ Extracted: {logo['filename']} - {logo['company']}")
        
        return extracted_count

    def run_detection(self):
        """
        Run the complete detection pipeline
        """
        print("Enhanced Logo Detection V2")
        print("=" * 50)
        print(f"Processing: {self.image_path}")
        print(f"Image size: {self.image.width}x{self.image.height}")
        
        # Step 1: Detect content regions
        print("\n1. Detecting content regions...")
        contours = self.detect_content_regions()
        print(f"   Found {len(contours)} potential regions")
        
        # Step 2: Refine bounding boxes
        print("\n2. Refining bounding boxes...")
        boxes = self.refine_bounding_boxes(contours)
        print(f"   Refined to {len(boxes)} valid boxes")
        
        # Step 3: Cluster into rows
        print("\n3. Clustering logos by rows...")
        logo_rows = self.cluster_logos_by_rows(boxes)
        print(f"   Organized into {len(logo_rows)} rows")
        
        # Step 4: Assign company names
        print("\n4. Assigning company names...")
        logos = self.assign_company_names(logo_rows)
        print(f"   Assigned {len(logos)} company names")
        
        # Step 5: Validate extractions
        print("\n5. Validating extractions...")
        validated_logos = self.validate_extractions(logos)
        valid_count = len([l for l in validated_logos if l['is_valid']])
        print(f"   {valid_count}/{len(validated_logos)} passed validation")
        
        # Step 6: Create preview
        print("\n6. Creating preview...")
        preview_file = self.create_visual_preview(validated_logos)
        print(f"   Preview saved: {preview_file}")
        
        # Step 7: Extract valid logos
        print("\n7. Extracting valid logos...")
        extracted_count = self.extract_valid_logos(validated_logos)
        print(f"   Extracted {extracted_count} valid logos")
        
        # Step 8: Save metadata
        print("\n8. Saving metadata...")
        metadata = {
            'source_image': self.image_path,
            'detection_method': 'Enhanced V2',
            'total_detections': len(validated_logos),
            'valid_extractions': valid_count,
            'logos': validated_logos
        }
        
        with open('enhanced_detection_results_v2.json', 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        print(f"   Metadata saved: enhanced_detection_results_v2.json")
        
        print("\n" + "=" * 50)
        print("🎯 DETECTION COMPLETE!")
        print(f"📊 Results: {valid_count}/{len(validated_logos)} logos extracted")
        print(f"📁 Output: enhanced-logos-v2/")
        print(f"🔍 Preview: {preview_file}")
        print("=" * 50)
        
        return validated_logos, preview_file

if __name__ == "__main__":
    detector = EnhancedLogoDetectorV2()
    results, preview = detector.run_detection()