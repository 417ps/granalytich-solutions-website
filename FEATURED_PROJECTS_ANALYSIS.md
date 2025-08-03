# Featured Projects Section Analysis - MWH Constructors Style

## Overview

This document analyzes the featured projects section from MWH Constructors website and provides implementation guidance for creating a similar feature for Granalytich Solutions Ltd.

## Key Features Analysis

### 1. Visual Design Elements

#### Grid Layout
- **4-column grid** on desktop (responsive to fewer columns on smaller screens)
- **Equal-height cards** maintaining aspect ratio
- **No visible borders** between cards in default state
- **Clean, minimal appearance** when not hovered

#### Image Treatment
- Full-bleed project images filling entire card space
- Professional photography showcasing actual project sites
- Images are the primary visual element (no text overlay in default state)

### 2. Hover Interaction Pattern

#### Hover Effect Behavior
- **Smooth slide-up animation** revealing project information
- **Semi-transparent dark overlay** (approximately rgba(0,0,0,0.8))
- **White text** on dark background for high contrast
- **Project title** appears prominently
- **"Learn More" or arrow icon** as call-to-action
- **Transition duration**: Approximately 300-400ms for smooth feel

#### Technical Implementation
```css
.project-card {
    position: relative;
    overflow: hidden;
    cursor: pointer;
}

.project-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: rgba(0, 0, 0, 0.85);
    color: white;
    padding: 30px;
    transform: translateY(100%);
    transition: transform 0.3s ease;
}

.project-card:hover .project-overlay {
    transform: translateY(0);
}
```

### 3. Project Detail Pages

#### Page Structure
- **Hero banner** with project image
- **Project metadata** (location, value, duration, client)
- **Detailed description** in readable paragraphs
- **Technical specifications** or key achievements
- **Related projects** section at bottom
- **Consistent navigation** back to projects grid

#### Content Organization
- Clear hierarchy with project name as H1
- Subheadings for different sections
- Bullet points for specifications
- Professional, technical writing style

## Implementation Guide for Granalytich Solutions

### 1. Adapting to Granalytich Brand

#### Color Scheme Integration
```css
:root {
    --primary-navy: #1e3a5f;
    --secondary-blue: #2e5a8a;
    --accent-gold: #d4af37;
    --overlay-dark: rgba(30, 58, 95, 0.9); /* Navy overlay */
}
```

#### Typography
- Use existing font stack from Granalytich site
- Maintain uppercase styling for project titles
- Keep consistent with current heading styles

### 2. Project Grid Structure

```html
<section class="featured-projects">
    <div class="container">
        <h2 class="section-title">FEATURED <span class="highlight">PROJECTS</span></h2>
        
        <div class="projects-grid">
            <div class="project-card">
                <img src="project-image.jpg" alt="Project Name">
                <div class="project-overlay">
                    <h3 class="project-title">Alternative Water Supply Program</h3>
                    <div class="project-value">$1.7B</div>
                    <a href="project-detail.html" class="project-link">
                        Learn More <span class="arrow">→</span>
                    </a>
                </div>
            </div>
            <!-- Additional project cards -->
        </div>
    </div>
</section>
```

### 3. Enhanced CSS Implementation

```css
.featured-projects {
    padding: 100px 0;
    background: #ffffff;
}

.projects-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 0;
    margin-top: 60px;
}

.project-card {
    position: relative;
    overflow: hidden;
    aspect-ratio: 4/3;
    background: #f5f5f5;
}

.project-card img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s ease;
}

.project-card:hover img {
    transform: scale(1.05);
}

.project-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(to top, rgba(30, 58, 95, 0.95), rgba(30, 58, 95, 0.85));
    color: white;
    padding: 30px;
    transform: translateY(100%);
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
}

.project-card:hover .project-overlay {
    transform: translateY(0);
}

.project-title {
    font-size: 1.25rem;
    font-weight: 700;
    margin-bottom: 10px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.project-value {
    font-size: 1.5rem;
    color: var(--accent-gold);
    font-weight: 700;
    margin-bottom: 15px;
}

.project-link {
    color: white;
    text-decoration: none;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    transition: gap 0.3s ease;
}

.project-link:hover {
    gap: 12px;
}

.project-link .arrow {
    font-size: 1.2em;
    transition: transform 0.3s ease;
}

.project-card:hover .project-link .arrow {
    transform: translateX(3px);
}
```

### 4. Mobile Responsiveness

```css
@media (max-width: 768px) {
    .projects-grid {
        grid-template-columns: 1fr;
        gap: 2px;
    }
    
    .project-card {
        aspect-ratio: 16/9;
    }
    
    .project-overlay {
        padding: 20px;
        transform: translateY(0);
        background: linear-gradient(to top, rgba(30, 58, 95, 0.9), transparent);
    }
    
    .project-title {
        font-size: 1.1rem;
    }
    
    .project-value {
        font-size: 1.25rem;
    }
}
```

### 5. Project Detail Page Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Project Name - Granalytich Solutions Ltd.</title>
    <!-- Include main site styles -->
</head>
<body>
    <!-- Navigation -->
    
    <section class="project-hero">
        <img src="project-hero.jpg" alt="Project Name">
        <div class="project-hero-overlay">
            <div class="container">
                <nav class="breadcrumb">
                    <a href="index.html">Home</a> / 
                    <a href="index.html#projects">Projects</a> / 
                    <span>Project Name</span>
                </nav>
                <h1>Alternative Water Supply Program</h1>
                <div class="project-meta">
                    <span class="meta-item">
                        <strong>Value:</strong> $1.7B
                    </span>
                    <span class="meta-item">
                        <strong>Duration:</strong> 2019-2024
                    </span>
                    <span class="meta-item">
                        <strong>Location:</strong> Colorado
                    </span>
                </div>
            </div>
        </div>
    </section>
    
    <section class="project-details">
        <div class="container">
            <div class="project-content">
                <h2>Project Overview</h2>
                <p>Detailed description of the project...</p>
                
                <h3>Key Achievements</h3>
                <ul>
                    <li>Achievement 1</li>
                    <li>Achievement 2</li>
                    <li>Achievement 3</li>
                </ul>
                
                <h3>Technical Specifications</h3>
                <div class="specs-grid">
                    <div class="spec-item">
                        <h4>Scope</h4>
                        <p>Description</p>
                    </div>
                    <div class="spec-item">
                        <h4>Challenges</h4>
                        <p>Description</p>
                    </div>
                </div>
            </div>
            
            <aside class="project-sidebar">
                <div class="project-info-box">
                    <h3>Project Information</h3>
                    <dl>
                        <dt>Client</dt>
                        <dd>Client Name</dd>
                        <dt>Services</dt>
                        <dd>Project Controls, Schedule Management</dd>
                        <dt>Contract Type</dt>
                        <dd>Type</dd>
                    </dl>
                </div>
            </aside>
        </div>
    </section>
    
    <!-- Related Projects -->
    <!-- Footer -->
</body>
</html>
```

## Implementation Recommendations

### 1. Image Requirements
- **Aspect Ratio**: 4:3 for desktop, 16:9 for mobile
- **Resolution**: Minimum 800x600px, optimized for web
- **Format**: WebP with JPEG fallback
- **Content**: Actual project photography, not stock images

### 2. Performance Optimization
- Lazy load images below the fold
- Use responsive images with srcset
- Implement smooth animations with will-change property
- Consider using Intersection Observer for animation triggers

### 3. Accessibility Considerations
- Ensure sufficient color contrast in overlays
- Add focus states for keyboard navigation
- Include descriptive alt text for all images
- Make hover content accessible on touch devices

### 4. Content Strategy
- Showcase 4-8 most impressive projects
- Mix project types (federal, municipal, infrastructure)
- Include project values to demonstrate scale
- Update regularly with recent completions

## Technical Implementation Notes

### JavaScript Enhancement (Optional)
```javascript
// Add staggered animation on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry, index) => {
        if (entry.isIntersecting) {
            setTimeout(() => {
                entry.target.classList.add('visible');
            }, index * 100);
        }
    });
}, observerOptions);

document.querySelectorAll('.project-card').forEach(card => {
    observer.observe(card);
});
```

### SEO Considerations
- Use semantic HTML structure
- Include schema markup for projects
- Optimize image file names and alt text
- Create unique meta descriptions for detail pages

## Conclusion

The MWH Constructors featured projects section succeeds through:
1. **Visual simplicity** - letting project images speak for themselves
2. **Elegant interaction** - smooth, purposeful animations
3. **Clear hierarchy** - obvious path from overview to details
4. **Professional presentation** - befitting large-scale infrastructure projects

Implementing this pattern for Granalytich Solutions will elevate the presentation of their impressive project portfolio while maintaining their established brand identity.