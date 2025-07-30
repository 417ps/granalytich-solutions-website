# Granalytich Solutions Ltd. - Logo Extraction Tool

Advanced computer vision tool for automatically extracting individual logos from composite logo images, developed for Granalytich Solutions Ltd.

## Features

- **Intelligent Blob Detection**: Uses OpenCV to detect individual logo elements
- **Connectivity Analysis**: Analyzes pixel connectivity to properly group text and graphics
- **DBSCAN Clustering**: Groups related logo parts using spatial clustering
- **Visual Validation**: HTML preview system for validating extraction boundaries
- **Automated Extraction**: Batch processes logos with proper padding and sizing

## Technology Stack

- **Computer Vision**: OpenCV, PIL/Pillow
- **Machine Learning**: scikit-learn (DBSCAN clustering)
- **Image Processing**: Morphological operations, contour detection
- **Visualization**: HTML/CSS preview system, matplotlib debugging

## Usage

1. Place your composite logo image as `client-logos-collection-v2.png`
2. Run: `python3 clustered_logo_detector.py`
3. View results in `clustered_extraction_preview.html`
4. Individual logos saved to `clustered-logos/` directory

## Algorithm

1. **Blob Detection**: Identifies colored regions using binary thresholding
2. **Initial Clustering**: Groups nearby blobs using DBSCAN with 120px minimum distance
3. **Connectivity Analysis**: Samples pixels between blob centers to detect continuous elements
4. **Merging**: Combines clusters with >30% colored pixels between centers
5. **Extraction**: Creates padded bounding boxes around final logo groups

## Results

- Successfully processes 52+ individual elements
- Intelligently clusters into 18+ complete logos
- Prevents text/graphic splitting (e.g., Los Alamos logo)
- Provides visual validation for quality assurance

## Deployment

Live demo available at the deployed Netlify site showing extraction results and methodology.

## Contact

- **Developed for**: Granalytich Solutions Ltd.
- **Email**: jjgranich@msn.com
- **Location**: Colorado Springs, CO

---

© 2024 Granalytich Solutions Ltd. All rights reserved.