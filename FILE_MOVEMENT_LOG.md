# File Movement Log

**Archive Date**: 2025-07-31 12:53:04  
**Archive Directory**: `archive-cleanup-20250731-125304/`

## Purpose
This log tracks all files moved during the codebase cleanup to help locate archived files if needed in the future.

## Archive Structure
```
archive-cleanup-20250731-125304/
├── html-versions/
│   ├── main-site-versions/    # Different versions of the main index.html
│   ├── test-layouts/          # Layout and feature test pages
│   └── granalytic-v3/         # Complete granalytic-v3 subdirectory
├── python-scripts/
│   ├── logo-extractors/       # Various logo extraction/processing scripts
│   └── utilities/             # Utility scripts (kept accessible)
├── documentation/
│   ├── reports/               # Logo detection and analysis reports
│   └── guides/                # Implementation and layout guides
└── temp-files/
    ├── previews/              # Preview and validation HTMLs
    └── debug/                 # Debug images and outputs
```

## File Movements

### HTML Files Archived

#### Main Site Versions
- `index-old-backup.html` → `archive-cleanup-20250731-125304/html-versions/main-site-versions/`
- `index-draft-modified.html` → `archive-cleanup-20250731-125304/html-versions/main-site-versions/`
- `index-v3.html` → `archive-cleanup-20250731-125304/html-versions/main-site-versions/`
- `index-v4-eunexus-inspired.html` → `archive-cleanup-20250731-125304/html-versions/main-site-versions/`
- `index-construction-inspired.html` → `archive-cleanup-20250731-125304/html-versions/main-site-versions/`

#### Test Layouts
- `about-section-options.html` → `archive-cleanup-20250731-125304/html-versions/test-layouts/`
- `client-logos-masonry-test.html` → `archive-cleanup-20250731-125304/html-versions/test-layouts/`
- `leadership-layout-test.html` → `archive-cleanup-20250731-125304/html-versions/test-layouts/`
- `logo_layout_options.html` → `archive-cleanup-20250731-125304/html-versions/test-layouts/`
- `option3_hexagonal.html` → `archive-cleanup-20250731-125304/html-versions/test-layouts/`
- `option5_spotlight_outline.html` → `archive-cleanup-20250731-125304/html-versions/test-layouts/`
- `simplified_tiered_layout.html` → `archive-cleanup-20250731-125304/html-versions/test-layouts/`

#### Validation/Preview Pages
- `blob_extraction_preview.html` → `archive-cleanup-20250731-125304/temp-files/previews/`
- `enhanced_detection_preview_v2.html` → `archive-cleanup-20250731-125304/temp-files/previews/`
- `logo_validation.html` → `archive-cleanup-20250731-125304/temp-files/previews/`
- `spaced_logo_validation.html` → `archive-cleanup-20250731-125304/temp-files/previews/`

#### Granalytic-v3 Directory
- `granalytic-v3/` (entire directory) → `archive-cleanup-20250731-125304/html-versions/granalytic-v3/`

### Python Scripts Archived

#### Logo Extractors/Processors
- `advanced_logo_extractor.py` → `archive-cleanup-20250731-125304/python-scripts/logo-extractors/`
- `background_remover.py` → `archive-cleanup-20250731-125304/python-scripts/logo-extractors/`
- `blob_center_detector.py` → `archive-cleanup-20250731-125304/python-scripts/logo-extractors/`
- `enhanced_logo_detector_v2.py` → `archive-cleanup-20250731-125304/python-scripts/logo-extractors/`
- `improved_logo_extractor.py` → `archive-cleanup-20250731-125304/python-scripts/logo-extractors/`
- `logo_color_converter.py` → `archive-cleanup-20250731-125304/python-scripts/logo-extractors/`
- `logo_extractor.py` → `archive-cleanup-20250731-125304/python-scripts/logo-extractors/`
- `refined_background_remover.py` → `archive-cleanup-20250731-125304/python-scripts/logo-extractors/`
- `refined_logo_extractor.py` → `archive-cleanup-20250731-125304/python-scripts/logo-extractors/`
- `spaced_logo_extractor.py` → `archive-cleanup-20250731-125304/python-scripts/logo-extractors/`

#### Utilities (Kept Accessible)
- `implement_layout_choice.py` → Kept in root
- `update_website_logos.py` → Kept in root

### Documentation Archived

#### Reports
- `DATA_CENTER_PROJECTS_RESEARCH.md` → `archive-cleanup-20250731-125304/documentation/reports/`
- `LOGO_DETECTION_REPORT.md` → `archive-cleanup-20250731-125304/documentation/reports/`

#### Guides
- `LOGO_LAYOUT_GUIDE.md` → `archive-cleanup-20250731-125304/documentation/guides/`

### Temporary Files Archived

#### Debug/Preview Images
- `blob_detection_debug.png` → `archive-cleanup-20250731-125304/temp-files/debug/`
- `detection_preview.png` → `archive-cleanup-20250731-125304/temp-files/debug/`
- `refined_extraction_preview.png` → `archive-cleanup-20250731-125304/temp-files/debug/`
- `client-logos-collection.png` → `archive-cleanup-20250731-125304/temp-files/debug/`
- `client-logos-collection-v2.png` → `archive-cleanup-20250731-125304/temp-files/debug/`
- `current-full-page.png` → `archive-cleanup-20250731-125304/temp-files/debug/`
- `current-services-section.png` → `archive-cleanup-20250731-125304/temp-files/debug/`

#### JSON Files
- `enhanced_detection_results_v2.json` → `archive-cleanup-20250731-125304/temp-files/debug/`
- `enhanced-logo-mapping-v2.json` → `archive-cleanup-20250731-125304/temp-files/debug/`
- `validation_report.json` → `archive-cleanup-20250731-125304/temp-files/debug/`

## Files Kept in Root
- `index.html` - Main website
- `README.md` - Project documentation
- `CLAUDE.md` - AI assistance guidelines
- `PROJECT_SUMMARY.md` - Project overview
- `DEPLOYMENT_GUIDE.md` - Deployment instructions
- `netlify.toml` - Netlify configuration
- `package.json` - Node dependencies
- `package-lock.json` - Dependency lock file
- `logo.png` - Company logo
- `implement_layout_choice.py` - Layout switching utility
- `update_website_logos.py` - Logo update utility
- `logos/` directory - All named logo files
- `source-documents/` - Original source materials
- `.gitignore` - Git configuration

## Quick Reference

### To find old website versions:
Look in: `archive-cleanup-20250731-125304/html-versions/main-site-versions/`

### To find logo processing scripts:
Look in: `archive-cleanup-20250731-125304/python-scripts/logo-extractors/`

### To find the granalytic-v3 site:
Look in: `archive-cleanup-20250731-125304/html-versions/granalytic-v3/`

### To find debug/preview files:
Look in: `archive-cleanup-20250731-125304/temp-files/`