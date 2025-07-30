#!/usr/bin/env python3
"""
Refined Background Remover for Logos
Advanced background removal with smooth edges and anti-aliasing preservation
"""

import os
from PIL import Image, ImageFilter
import numpy as np
from scipy import ndimage

def refined_remove_background(image_path, output_path, bg_threshold=230, edge_threshold=50):
    """
    Advanced background removal with smooth edges
    bg_threshold: Main background detection threshold (lower = more aggressive)
    edge_threshold: Edge smoothing threshold for anti-aliasing
    """
    with Image.open(image_path) as img:
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Convert to numpy array
        data = np.array(img, dtype=np.float32)
        rgb = data[:, :, :3]
        alpha = data[:, :, 3]
        
        # Method 1: Brightness-based detection
        brightness = np.mean(rgb, axis=2)
        
        # Method 2: Color similarity to white
        white_similarity = np.sqrt(np.sum((rgb - 255)**2, axis=2))
        
        # Method 3: Detect corners/edges (likely logo content)
        gray = np.mean(rgb, axis=2)
        
        # Apply Gaussian blur to reduce noise
        gray_blurred = ndimage.gaussian_filter(gray, sigma=1.0)
        
        # Calculate gradients (edges)
        grad_x = ndimage.sobel(gray_blurred, axis=1)
        grad_y = ndimage.sobel(gray_blurred, axis=0)
        gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        
        # Normalize gradient magnitude
        if gradient_magnitude.max() > 0:
            gradient_magnitude = gradient_magnitude / gradient_magnitude.max() * 255
        
        # Create sophisticated background mask
        # Pixels are background if:
        # 1. They're bright (close to white)
        # 2. They have low color variation 
        # 3. They're not near edges (low gradient)
        
        brightness_mask = brightness >= bg_threshold
        white_similarity_mask = white_similarity <= edge_threshold
        low_gradient_mask = gradient_magnitude <= 20  # Low edge activity
        
        # Combine conditions: background pixels must meet all criteria
        background_mask = brightness_mask & white_similarity_mask & low_gradient_mask
        
        # Apply morphological operations to clean up the mask
        from scipy.ndimage import binary_erosion, binary_dilation
        
        # Clean up small artifacts
        background_mask = binary_erosion(background_mask, iterations=1)
        background_mask = binary_dilation(background_mask, iterations=1)
        
        # Create smooth alpha transitions
        new_alpha = alpha.copy()
        
        # For background pixels, set alpha to 0
        new_alpha[background_mask] = 0
        
        # For edge pixels, create gradual transparency
        edge_distance = ndimage.distance_transform_edt(~background_mask)
        edge_pixels = (edge_distance > 0) & (edge_distance <= 3)  # 3-pixel transition zone
        
        # Apply smooth transition in edge areas
        for i in range(1, 4):
            transition_pixels = (edge_distance > i-1) & (edge_distance <= i) & edge_pixels
            transition_alpha = max(0, 255 * (1 - i/4))  # Gradual fade
            new_alpha[transition_pixels] = np.minimum(new_alpha[transition_pixels], transition_alpha)
        
        # Apply Gaussian blur to alpha channel for even smoother edges
        new_alpha = ndimage.gaussian_filter(new_alpha, sigma=0.5)
        
        # Ensure alpha values are in valid range
        new_alpha = np.clip(new_alpha, 0, 255)
        
        # Create final image data
        final_data = data.copy()
        final_data[:, :, 3] = new_alpha
        final_data = np.clip(final_data, 0, 255).astype(np.uint8)
        
        # Convert back to PIL Image and save
        result_img = Image.fromarray(final_data, 'RGBA')
        
        # Apply a slight blur to the entire image to smooth any remaining jaggedness
        result_img = result_img.filter(ImageFilter.GaussianBlur(radius=0.3))
        
        result_img.save(output_path, 'PNG')

def process_logos_refined(input_dir):
    """Process all PNG files with refined background removal"""
    
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
                refined_remove_background(input_path, output_path, bg_threshold=225, edge_threshold=60)
                print(f"Refined processing: {filename}")
                processed_count += 1
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    
    return processed_count

if __name__ == "__main__":
    # Set paths
    input_directory = os.path.expanduser("~/Downloads/granalytic-logos")
    
    print("Refining background removal with advanced edge detection...")
    print(f"Processing directory: {input_directory}")
    print("Using:")
    print("- Edge detection and gradient analysis")
    print("- Morphological operations for cleanup")
    print("- Gaussian smoothing for anti-aliasing") 
    print("- Multi-level alpha transitions")
    print()
    
    processed = process_logos_refined(input_directory)
    
    print(f"\nRefined background removal complete!")
    print(f"Processed {processed} logo files")
    print("Logos now have smooth, professional edges with preserved anti-aliasing")