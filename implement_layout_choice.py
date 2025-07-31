#!/usr/bin/env python3
"""
Logo Layout Implementation Script
Allows easy switching between different logo layout options for the website
"""

import json
import shutil
from datetime import datetime

def load_logo_mapping():
    """Load the enhanced logo mapping"""
    with open('enhanced-logo-mapping-v2.json', 'r') as f:
        return json.load(f)

def backup_current_layout():
    """Create backup of current index.html"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"index_backup_{timestamp}.html"
    shutil.copy('index.html', backup_name)
    print(f"✅ Current layout backed up as: {backup_name}")
    return backup_name

def implement_ticker_layout():
    """Option 1: Animated Ticker Layout"""
    logos = load_logo_mapping()['logos']
    
    # Generate ticker HTML
    ticker_items = []
    for logo in logos:
        item = f'''                <div class="logo-ticker-item" data-company="{logo['company']}">
                    <img src="logos/{logo['filename']}" alt="{logo['alt']}" loading="lazy">
                </div>'''
        ticker_items.append(item)
    
    ticker_html = f'''    <!-- Logo Ticker Section -->
    <section class="logo-ticker-section">
        <div class="logo-ticker-container">
            <h2 class="section-title-logos">TRUSTED BY <span class="highlight">INDUSTRY LEADERS</span></h2>
            <div class="logo-ticker">
                <!-- First set of logos -->
{chr(10).join(ticker_items)}
                
                <!-- Duplicate set for seamless loop -->
{chr(10).join(ticker_items)}
            </div>
        </div>
    </section>'''

    ticker_css = '''
        /* Logo Ticker Section */
        .logo-ticker-section {
            background-color: var(--white);
            padding: 40px 0 30px;
            overflow: hidden;
        }

        .logo-ticker-container {
            position: relative;
            width: 100%;
        }

        .logo-ticker {
            display: flex;
            gap: 4rem;
            animation: scroll-logos 40s linear infinite;
            will-change: transform;
        }

        .logo-ticker-item {
            flex-shrink: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 60px;
            padding: 0 2rem;
            transition: all 0.4s ease;
            cursor: pointer;
            position: relative;
        }

        .logo-ticker-item img {
            max-height: 50px;
            width: auto;
            max-width: 150px;
            object-fit: contain;
            transition: all 0.4s ease;
        }

        .logo-ticker-item:hover img {
            transform: scale(1.05);
        }

        .logo-ticker-item:hover::after {
            content: attr(data-company);
            position: absolute;
            bottom: -35px;
            left: 50%;
            transform: translateX(-50%);
            background: var(--primary-navy);
            color: var(--white);
            padding: 0.5rem 1rem;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 600;
            white-space: nowrap;
            z-index: 10;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        }

        @keyframes scroll-logos {
            0% {
                transform: translateX(0);
            }
            100% {
                transform: translateX(-50%);
            }
        }

        /* Mobile optimization */
        @media (max-width: 768px) {
            .logo-ticker {
                gap: 2rem;
            }
            
            .logo-ticker-item {
                padding: 0 1rem;
            }
            
            .logo-ticker-item img {
                max-height: 40px;
                max-width: 120px;
            }
        }'''
    
    return ticker_html, ticker_css

def implement_sector_layout():
    """Option 2: Sector Categories Layout"""
    logos = load_logo_mapping()['logos']
    
    # Organize by sectors
    sectors = {
        'federal': {'title': '🏛️ Federal Agencies', 'logos': []},
        'private': {'title': '🏗️ Engineering & Construction', 'logos': []},
        'government': {'title': '🏢 Government & Utilities', 'logos': []},
        'academic': {'title': '🎓 Academic Partners', 'logos': []}
    }
    
    for logo in logos:
        sector = logo.get('sector', 'private')
        if sector in sectors:
            sectors[sector]['logos'].append(logo)
    
    # Generate sector HTML
    sector_cards = []
    for sector_key, sector_data in sectors.items():
        if sector_data['logos']:
            logo_items = []
            for logo in sector_data['logos'][:8]:  # Limit to 8 per sector
                logo_items.append(f'''                        <div class="sector-logo">
                            <img src="logos/{logo['filename']}" alt="{logo['alt']}" loading="lazy">
                        </div>''')
            
            card = f'''                <div class="sector-card">
                    <h3 class="sector-title">{sector_data['title']}</h3>
                    <div class="sector-logos">
{chr(10).join(logo_items)}
                    </div>
                </div>'''
            sector_cards.append(card)
    
    sector_html = f'''    <!-- Sector Categories Section -->
    <section class="sector-logos-section">
        <div class="sector-logos-container">
            <h2 class="section-title-logos">TRUSTED BY <span class="highlight">INDUSTRY LEADERS</span></h2>
            <p class="section-subtitle">Specialized expertise across critical infrastructure sectors</p>
            <div class="sector-grid">
{chr(10).join(sector_cards)}
            </div>
        </div>
    </section>'''

    sector_css = '''
        /* Sector Categories Section */
        .sector-logos-section {
            background-color: var(--white);
            padding: 80px 0;
        }

        .sector-logos-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            text-align: center;
        }

        .section-subtitle {
            font-size: 16px;
            color: #666;
            margin-bottom: 60px;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }

        .sector-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 40px;
            margin-top: 40px;
        }

        .sector-card {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            border-top: 4px solid var(--accent-gold);
            transition: transform 0.3s ease;
        }

        .sector-card:hover {
            transform: translateY(-5px);
        }

        .sector-title {
            font-size: 1.3rem;
            color: var(--primary-navy);
            margin-bottom: 25px;
            font-weight: 600;
        }

        .sector-logos {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }

        .sector-logo {
            padding: 15px;
            background: var(--light-gray);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            min-height: 60px;
        }

        .sector-logo:hover {
            background: white;
            box-shadow: 0 3px 15px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }

        .sector-logo img {
            max-height: 35px;
            max-width: 120px;
            object-fit: contain;
        }

        /* Mobile optimization */
        @media (max-width: 768px) {
            .sector-grid {
                grid-template-columns: 1fr;
            }
            
            .sector-logos {
                grid-template-columns: 1fr;
            }
        }'''
    
    return sector_html, sector_css

def implement_spotlight_layout():
    """Option 5: Spotlight Feature Layout"""
    logos = load_logo_mapping()['logos']
    
    # Select premium clients for spotlight
    premium_clients = ['logo_09.png', 'logo_06.png', 'logo_02.png', 'logo_22.png']  # NASA, DOE, Los Alamos, Raytheon
    premium_logos = [logo for logo in logos if logo['filename'] in premium_clients]
    regular_logos = [logo for logo in logos if logo['filename'] not in premium_clients]
    
    # Generate spotlight HTML
    premium_items = []
    for logo in premium_logos:
        premium_items.append(f'''                        <div class="spotlight-logo">
                            <img src="logos/{logo['filename']}" alt="{logo['alt']}" loading="lazy">
                        </div>''')
    
    regular_items = []
    for logo in regular_logos[:12]:  # Limit regular items
        regular_items.append(f'''                <div class="spotlight-regular">
                    <img src="logos/{logo['filename']}" alt="{logo['alt']}" loading="lazy">
                </div>''')
    
    spotlight_html = f'''    <!-- Spotlight Feature Section -->
    <section class="spotlight-logos-section">
        <div class="spotlight-logos-container">
            <h2 class="section-title-logos">TRUSTED BY <span class="highlight">INDUSTRY LEADERS</span></h2>
            <div class="spotlight-grid">
                <div class="spotlight-featured">
                    <h3 class="spotlight-title">Premier Federal Clients</h3>
                    <p>Mission-critical partnerships with the nation's leading agencies</p>
                    <div class="spotlight-logos">
{chr(10).join(premium_items)}
                    </div>
                </div>
{chr(10).join(regular_items)}
            </div>
        </div>
    </section>'''

    spotlight_css = '''
        /* Spotlight Feature Section */
        .spotlight-logos-section {
            background-color: var(--white);
            padding: 80px 0;
        }

        .spotlight-logos-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
            text-align: center;
        }

        .spotlight-grid {
            display: grid;
            grid-template-columns: repeat(8, 1fr);
            gap: 20px;
            align-items: start;
            margin-top: 50px;
        }

        .spotlight-featured {
            grid-column: span 4;
            grid-row: span 2;
            background: linear-gradient(135deg, var(--primary-navy), var(--secondary-blue));
            color: white;
            padding: 40px;
            border-radius: 12px;
            text-align: center;
        }

        .spotlight-title {
            font-size: 1.8rem;
            margin-bottom: 20px;
            color: var(--accent-gold);
        }

        .spotlight-featured p {
            margin-bottom: 30px;
            opacity: 0.9;
        }

        .spotlight-logos {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
        }

        .spotlight-logo {
            background: rgba(255,255,255,0.1);
            padding: 20px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 80px;
        }

        .spotlight-logo img {
            max-height: 50px;
            max-width: 120px;
            object-fit: contain;
            filter: brightness(0) invert(1);
        }

        .spotlight-regular {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 3px 15px rgba(0,0,0,0.1);
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 80px;
            transition: all 0.3s ease;
        }

        .spotlight-regular:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }

        .spotlight-regular img {
            max-height: 40px;
            max-width: 100px;
            object-fit: contain;
        }

        /* Mobile optimization */
        @media (max-width: 768px) {
            .spotlight-grid {
                grid-template-columns: 1fr;
            }
            
            .spotlight-featured {
                grid-column: span 1;
                grid-row: span 1;
            }
            
            .spotlight-logos {
                grid-template-columns: 1fr;
            }
        }'''
    
    return spotlight_html, spotlight_css

def update_website_with_layout(layout_choice):
    """Update the website with chosen layout"""
    print(f"\n🔄 Implementing Layout Option: {layout_choice}")
    
    # Create backup
    backup_file = backup_current_layout()
    
    # Read current HTML
    with open('index.html', 'r') as f:
        html_content = f.read()
    
    # Generate layout based on choice
    if layout_choice == "ticker":
        new_html, new_css = implement_ticker_layout()
        layout_name = "Animated Ticker"
    elif layout_choice == "sectors":
        new_html, new_css = implement_sector_layout()
        layout_name = "Sector Categories"
    elif layout_choice == "spotlight":
        new_html, new_css = implement_spotlight_layout()
        layout_name = "Spotlight Feature"
    else:
        print("❌ Invalid layout choice!")
        return False
    
    # Find and replace the client logos section
    start_marker = "<!-- Client Logos Section -->"
    end_marker = "<!-- Three Features Section -->"
    
    start_pos = html_content.find(start_marker)
    end_pos = html_content.find(end_marker)
    
    if start_pos == -1 or end_pos == -1:
        print("❌ Could not find logo section markers in HTML")
        return False
    
    # Replace the section
    updated_html = html_content[:start_pos] + new_html + "\n\n    " + html_content[end_pos:]
    
    # Update CSS (find and replace client logos CSS)
    css_start = updated_html.find("/* Client Logos Masonry Section */")
    if css_start != -1:
        # Find the end of the CSS section (next major comment)
        css_end = updated_html.find("/* Footer */", css_start)
        if css_end != -1:
            updated_html = updated_html[:css_start] + new_css + "\n\n        " + updated_html[css_end:]
    
    # Write updated HTML
    with open('index.html', 'w') as f:
        f.write(updated_html)
    
    print(f"✅ Successfully implemented {layout_name} layout!")
    print(f"📁 Backup saved as: {backup_file}")
    return True

def main():
    """Main implementation script"""
    print("🎨 Logo Layout Implementation Tool")
    print("=" * 50)
    
    print("\nAvailable Layout Options:")
    print("1. ticker    - Animated scrolling ticker")
    print("2. sectors   - Organized by industry sectors")  
    print("3. spotlight - Featured premium clients")
    print("4. current   - Keep current masonry layout")
    
    choice = input("\nEnter your choice (ticker/sectors/spotlight/current): ").lower().strip()
    
    if choice == "current":
        print("✅ Keeping current layout - no changes made")
        return
    
    if choice in ["ticker", "sectors", "spotlight"]:
        success = update_website_with_layout(choice)
        if success:
            print(f"\n🎉 Layout successfully updated!")
            print("🌐 You can now view the changes in your browser")
            print("📝 Check the preview at: logo_layout_options.html")
        else:
            print("\n❌ Layout update failed!")
    else:
        print("❌ Invalid choice. Please run the script again.")

if __name__ == "__main__":
    main()