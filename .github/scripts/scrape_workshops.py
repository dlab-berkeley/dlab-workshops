#!/usr/bin/env python3
"""
Scrape upcoming workshops from D-Lab EventSpark page
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import pytz
import re
import os

# URL to scrape
EVENTS_URL = "https://dlab.my.salesforce-sites.com/events"

# Output file
OUTPUT_FILE = "_data/upcoming_workshops.json"

def parse_datetime_string(date_str, time_str):
    """Parse date and time strings into ISO format"""
    try:
        # Example: "Aug 19, 2025" and "10:00 AM - 12:00 PM (GMT-7:00)"
        # Extract start time
        time_match = re.match(r'(\d{1,2}:\d{2}\s*[AP]M)', time_str)
        if time_match:
            start_time = time_match.group(1)
            # Combine date and time
            datetime_str = f"{date_str} {start_time}"
            # Parse with timezone awareness
            dt = datetime.strptime(datetime_str, "%b %d, %Y %I:%M %p")
            # Assume Pacific Time
            pacific = pytz.timezone('America/Los_Angeles')
            dt = pacific.localize(dt)
            return dt.isoformat()
    except Exception as e:
        print(f"Error parsing datetime: {e}")
    return None


def extract_workshop_info(workshop_div):
    """Extract workshop information from a div element"""
    try:
        # Find the title - it's typically in a heading or strong element
        title_elem = workshop_div.find(['h2', 'h3', 'h4', 'strong'])
        if not title_elem:
            # Try finding by class or other methods
            title_elem = workshop_div.find(class_=re.compile('title|heading', re.I))

        title = title_elem.text.strip() if title_elem else "Unknown Workshop"

        # Find date and time - look for calendar icon or date pattern
        date_text = ""
        time_text = ""

        # Look for date patterns
        text_content = workshop_div.get_text()
        date_match = re.search(r'([A-Za-z]{3}\s+\d{1,2},\s+\d{4})', text_content)
        if date_match:
            date_text = date_match.group(1)

        # Look for time patterns
        time_match = re.search(r'(\d{1,2}:\d{2}\s*[AP]M\s*-\s*\d{1,2}:\d{2}\s*[AP]M\s*\([^)]+\))', text_content)
        if time_match:
            time_text = time_match.group(1)

        # Find registration link - look for links containing /events/event/home/
        register_link = None
        links = workshop_div.find_all('a', href=True)
        for link in links:
            href = link['href']
            # Look for EventSpark event links
            if '/events/event/home/' in href or 'event/home/' in href:
                if not href.startswith('http'):
                    href = f"https://dlab.my.salesforce-sites.com{href}"
                register_link = href
                break
            # Also check for register/signup type links
            elif any(term in href.lower() for term in ['register', 'signup', 'book']):
                if not href.startswith('http'):
                    href = f"https://dlab.my.salesforce-sites.com{href}"
                register_link = href

        # Parse datetime
        datetime_iso = None
        if date_text and time_text:
            datetime_iso = parse_datetime_string(date_text, time_text)

        return {
            "title": title,
            "date": date_text,
            "time": time_text,
            "datetime_iso": datetime_iso,
            "registration_url": register_link,
            "scraped_at": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        print(f"Error extracting workshop info: {e}")
        return None


def scrape_workshops():
    """Main function to scrape workshops"""
    print(f"Fetching workshops from {EVENTS_URL}")

    try:
        response = requests.get(EVENTS_URL, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find workshop containers
        # Based on the screenshot, workshops seem to be in divs with specific structure
        workshops = []

        # Look for workshop containers based on EventSpark structure
        # First try to find by class names that might contain event info
        workshop_containers = []

        # Try finding containers with links to /events/event/home/
        for link in soup.find_all('a', href=re.compile(r'/events/event/home/')):
            # Get the parent container that likely holds all workshop info
            parent = link.find_parent('div')
            if parent and parent not in workshop_containers:
                # Look for a container that has both title and date
                container = parent
                # Keep going up until we find a reasonable container
                while container and container.parent:
                    text = container.get_text()
                    if (re.search(r'[A-Za-z]{3}\s+\d{1,2},\s+\d{4}', text) and
                        any(keyword in text.upper() for keyword in ['FUNDAMENTALS', 'WORKSHOP', 'PYTHON', 'R ', 'DATA', 'MACHINE','API'])):
                        workshop_containers.append(container)
                        break
                    container = container.parent

        # Also try standard class-based search
        if not workshop_containers:
            workshop_containers = soup.find_all('div', class_=re.compile('workshop|event|session', re.I))

        # If still nothing, look for divs containing workshop patterns
        if not workshop_containers:
            for div in soup.find_all('div'):
                text = div.get_text()
                if (any(keyword in text.upper() for keyword in ['FUNDAMENTALS', 'WORKSHOP', 'PYTHON', 'R ', 'DATA']) and
                    re.search(r'[A-Za-z]{3}\s+\d{1,2},\s+\d{4}', text) and
                    div.find('a', href=True)):  # Has a link
                    workshop_containers.append(div)

        print(f"Found {len(workshop_containers)} potential workshop containers")

        for container in workshop_containers:
            workshop_info = extract_workshop_info(container)
            if workshop_info and workshop_info['title'] != "Unknown Workshop":
                workshops.append(workshop_info)
                print(f"Extracted: {workshop_info['title']}")

        # Sort by date
        workshops.sort(key=lambda x: x['datetime_iso'] or '')

        # Filter out past workshops
        current_time = datetime.now(timezone.utc)
        upcoming_workshops = []
        for workshop in workshops:
            if workshop['datetime_iso']:
                workshop_time = datetime.fromisoformat(workshop['datetime_iso'])
                if workshop_time > current_time:
                    upcoming_workshops.append(workshop)

        # Prepare output
        output = {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "total_workshops": len(upcoming_workshops),
            "workshops": upcoming_workshops
        }

        # Ensure directory exists
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

        # Write to file
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"Successfully saved {len(upcoming_workshops)} upcoming workshops to {OUTPUT_FILE}")

    except Exception as e:
        print(f"Error scraping workshops: {e}")
        # Create empty file to prevent build errors
        output = {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "total_workshops": 0,
            "workshops": [],
            "error": str(e)
        }
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(output, f, indent=2)

if __name__ == "__main__":
    scrape_workshops()
