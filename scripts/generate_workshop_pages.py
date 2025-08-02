#!/usr/bin/env python3
"""
Generate individual workshop pages for all workshops in the data
"""

import yaml
from pathlib import Path
import re

def slugify(text):
    """Convert text to URL-friendly slug"""
    # Convert to lowercase and replace spaces with hyphens
    slug = text.lower().replace(' ', '-')
    # Remove special characters except hyphens
    slug = re.sub(r'[^a-z0-9\-]', '', slug)
    # Replace multiple hyphens with single hyphen
    slug = re.sub(r'-+', '-', slug)
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    return slug

def generate_workshop_pages():
    """Generate workshop pages for all workshops"""
    # Load workshop data
    project_root = Path(__file__).parent.parent
    workshops_file = project_root / '_data' / 'workshops.yml'
    
    with open(workshops_file, 'r') as f:
        data = yaml.safe_load(f)
    
    workshops = data.get('workshops', [])
    workshop_dir = project_root / 'workshop'
    workshop_dir.mkdir(exist_ok=True)
    
    created_count = 0
    
    for workshop in workshops:
        title = workshop.get('title', '')
        if not title:
            continue
            
        slug = slugify(title)
        workshop_file = workshop_dir / f'{slug}.md'
        
        # Skip if file already exists
        if workshop_file.exists():
            continue
            
        # Create workshop page content
        content = f"""---
layout: workshop
title: "{title}"
workshop_title: "{title}"
permalink: /workshop/{slug}/
---
"""
        
        # Write the file
        with open(workshop_file, 'w') as f:
            f.write(content)
        
        created_count += 1
        print(f"Created: {workshop_file}")
    
    print(f"\nGenerated {created_count} workshop pages")
    print(f"Total workshops: {len(workshops)}")

if __name__ == "__main__":
    generate_workshop_pages()