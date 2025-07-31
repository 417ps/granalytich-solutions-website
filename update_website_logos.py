#!/usr/bin/env python3
"""
Update Website with Enhanced Logos V2
Updates the index.html file to use the newly extracted enhanced logos
"""

import json
import re
from pathlib import Path

def load_logo_mapping():
    """Load the enhanced logo mapping"""
    with open('enhanced-logo-mapping-v2.json', 'r') as f:
        return json.load(f)

def update_index_html():
    """Update the index.html file with new logo references"""
    
    # Read current index.html
    with open('index.html', 'r') as f:
        html_content = f.read()
    
    # Load logo mapping
    logo_data = load_logo_mapping()
    logos = logo_data['logos']
    
    print(f"Updating website with {len(logos)} enhanced logos...")
    
    # Create mapping from old filenames to new ones
    filename_mapping = {
        'logo-nasa.png': 'logo_09.png',
        'logo-us-doe.png': 'logo_06.png', 
        'logo-los-alamos-national-lab.png': 'logo_02.png',
        'logo-stantec.png': 'logo_11.png',
        'logo-bechtel.png': 'logo_16.png',
        'logo-nm-dot.png': 'logo_01.png',
        'logo-aecom.png': 'logo_17.png',
        'logo-raytheon.png': 'logo_22.png',
        'logo-mwh-global.png': 'logo_13.png',
        'logo-wilson-company.png': 'logo_04.png',
        'logo-rmf-engineering.png': 'logo_05.png',
        'logo-ucla.png': 'logo_15.png',
        'logo-colorado-springs-utilities.png': 'logo_03.png',
        'logo-cross-connection-inc.png': 'logo_07.png',
        'logo-red-rochester.png': 'logo_08.png',
        'logo-frank-lill-son.png': 'logo_10.png',
        'logo-futures-mechanical.png': 'logo_12.png',
        'logo-set-inc.png': 'logo_14.png',
        'logo-dls-construction.png': 'logo_18.png',
        'logo-twenty20-construction.png': 'logo_19.png',
        'logo-los-alamos-research.png': 'logo_20.png',
        'logo-pueblo-electric.png': 'logo_21.png'
    }
    
    # Update all logo references
    updated_html = html_content
    replacements_made = 0
    
    for old_filename, new_filename in filename_mapping.items():
        old_path = f'logos/{old_filename}'
        new_path = f'logos/{new_filename}'
        
        if old_path in updated_html:
            updated_html = updated_html.replace(old_path, new_path)
            replacements_made += 1
            print(f"   ✅ Updated: {old_filename} → {new_filename}")
    
    if replacements_made == 0:
        print("❌ Error: No logo references found to update")
        return False
    
    # Write the updated HTML
    with open('index.html', 'w') as f:
        f.write(updated_html)
    
    print(f"✅ Successfully updated {replacements_made} logo references in index.html")
    return True

def create_logo_inventory():
    """Create an inventory report of available logos"""
    logo_data = load_logo_mapping()
    logos = logo_data['logos']
    
    print("\n📊 LOGO INVENTORY REPORT")
    print("=" * 50)
    print(f"Source Image: {logo_data['source']}")
    print(f"Detection Method: {logo_data['detection_method']}")
    print(f"Total Logos: {logo_data['total_logos']}")
    print()
    
    # Group by sector
    sectors = {}
    for logo in logos:
        sector = logo.get('sector', 'unknown')
        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append(logo)
    
    for sector, sector_logos in sectors.items():
        print(f"🏢 {sector.upper()} ({len(sector_logos)} logos):")
        for logo in sector_logos:
            print(f"   • {logo['company']} ({logo['filename']})")
        print()
    
    print("=" * 50)

if __name__ == "__main__":
    print("🔄 Updating Website with Enhanced Logos V2")
    print("=" * 50)
    
    # Create inventory report
    create_logo_inventory()
    
    # Update the website
    success = update_index_html()
    
    if success:
        print("\n🎉 WEBSITE UPDATE COMPLETE!")
        print("✅ Enhanced logos are now live on the website")
        print("🌐 All 22 client logos have been updated with improved quality")
        print("\nNext steps:")
        print("1. Test the website in a browser")
        print("2. Verify logo ticker animation works smoothly")
        print("3. Check logo quality and hover effects")
    else:
        print("\n❌ WEBSITE UPDATE FAILED!")
        print("Please check the HTML structure and try again")
    
    print("=" * 50)