#!/usr/bin/env python3
"""
Fetch workshop catalog from Google Sheets and update workshops.yml
"""

import json
import os
import sys
import yaml
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def get_google_sheets_service():
    """
    Create and return Google Sheets service using service account
    Supports both service account file (GOOGLE_APPLICATION_CREDENTIALS) and JSON string (GOOGLE_SERVICE_ACCOUNT_KEY)
    """
    try:
        credentials = None
        
        # Try service account file first (for local development)
        if os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
            credentials = service_account.Credentials.from_service_account_file(
                os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'),
                scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
            )
        # Fall back to JSON string (for GitHub Actions)
        elif os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY'):
            service_account_info = json.loads(os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY'))
            credentials = service_account.Credentials.from_service_account_info(
                service_account_info,
                scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
            )
        else:
            raise ValueError("Neither GOOGLE_APPLICATION_CREDENTIALS nor GOOGLE_SERVICE_ACCOUNT_KEY environment variable is set")
        
        service = build('sheets', 'v4', credentials=credentials)
        return service
        
    except Exception as e:
        print(f"Error creating Google Sheets service: {e}")
        return None

def fetch_google_sheet_data(sheet_id: str, range_name: str = 'A:ZZ') -> List[Dict]:
    """
    Fetch data from a Google Sheet using service account authentication
    """
    service = get_google_sheets_service()
    if not service:
        return []
    
    try:
        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
        values = result.get('values', [])
        
        if not values:
            print('No data found in sheet.')
            return []
        
        # First row contains headers
        headers = values[0]
        
        # Convert rows to dictionaries
        data = []
        for row in values[1:]:
            # Pad row with empty strings if it's shorter than headers
            row_padded = row + [''] * (len(headers) - len(row))
            row_dict = {headers[i]: row_padded[i] for i in range(len(headers))}
            data.append(row_dict)
        
        return data
        
    except HttpError as e:
        print(f"An error occurred accessing Google Sheets: {e}")
        return []
    except Exception as e:
        print(f"Error fetching Google Sheet data: {e}")
        return []

def create_short_description(full_description: str, max_length: int = 150) -> str:
    """
    Create a short description from full description by stripping HTML and truncating
    """
    if not full_description:
        return ''
    
    # Remove HTML tags
    clean_text = re.sub(r'<[^>]+>', '', full_description)
    
    # Clean up extra whitespace
    clean_text = ' '.join(clean_text.split())
    
    # Truncate to max length
    if len(clean_text) <= max_length:
        return clean_text
    
    # Find the last space before max_length to avoid cutting words
    truncated = clean_text[:max_length]
    last_space = truncated.rfind(' ')
    if last_space > 0:
        truncated = truncated[:last_space]
    
    return truncated + '...'

def title_to_github_repo(title: str) -> str:
    """
    Convert workshop title to GitHub repository name
    Based on existing patterns in the repository
    """
    # Common transformations
    repo_name = title
    
    # Remove parts specifications for repo names
    repo_name = repo_name.replace(': Parts 1-2', '')
    repo_name = repo_name.replace(': Parts 1-3', '')
    repo_name = repo_name.replace(': Parts 1-4', '')
    repo_name = repo_name.replace(': Parts 4-6', '')
    
    # Specific mappings based on existing repos
    title_mappings = {
        'Python Data Visualization': 'Python-Data-Visualization',
        'Command Line Fundamentals': 'Command-Line-Fundamentals',
        'Python GPT Fundamentals': 'GPT-Fundamentals',
        'LLMs for Exploratory Research': 'LLMs-Exploratory-Research',
        'Python APIs for Large Language Models': 'Python-APIs-for-Large-Language-Models',
        'Python Fundamentals': 'Python-Fundamentals',
        'Python Web APIs': 'Python-Web-APIs',
        'Python Web Scraping': 'Python-Web-Scraping',
        'Python SQL Fundamentals': 'Python-SQL-Fundamentals',
        'Python Data Wrangling and Manipulation with Pandas': 'Python-Data-Wrangling',
        'Python Machine Learning Fundamentals': 'Python-Machine-Learning',
        'R Fundamentals': 'R-Fundamentals',
        'R Data Wrangling and Manipulation': 'R-Data-Wrangling',
        'R Data Visualization': 'R-Data-Visualization',
        'R Machine Learning with tidymodels': 'R-Machine-Learning',
        'Git Fundamentals': 'Git-Fundamentals',
        'GitHub Fundamentals': 'GitHub-Fundamentals'
    }
    
    if repo_name in title_mappings:
        return title_mappings[repo_name]
    
    # Default transformation: replace spaces with hyphens, remove colons
    repo_name = repo_name.replace(' ', '-').replace(':', '').replace('(', '').replace(')', '')
    return repo_name

def parse_workshop_catalog(raw_data: List[Dict]) -> List[Dict]:
    """
    Parse and transform raw Google Sheets data into workshop catalog format
    Expected columns:
    - Workshop_Name__c: Workshop title
    - Category__c: Primary category (python, r, ai, sql, qualitative, other)
    - Secondary_Category__c: Secondary category (optional)
    - Description__c: Full description of the workshop and its learning goals
    - Duration_min__c: Duration in minutes
    - Prerequisites__c: Text with which workshops we recommend taking first
    - Software_Requirements__c: Text on software requirements for the workshop
    - Cloud_option__c: Text saying whether the workshop has a cloud option
    - dlab_Workshop_Materials_text__c: The URL to the github repo
    - Difficulty_Level__c: Text with difficulty level, introductory/intermediate/advanced
    - dlab_Before_you_join__c: Text on what participants need to know before they join the workshop
    """
    workshops = []
    
    # Map category names to lowercase versions used in the site
    category_map = {
        'Python': 'python',
        'R Programming': 'r',
        'AI': 'ai',
        'SQL': 'sql',
        'Qualitative': 'qualitative',
        'Other': 'other'
    }
    
    for row in raw_data:
        try:
            # Skip empty rows
            if not row.get('Workshop_Name__c'):
                continue
            
            # Get workshop data
            title = row.get('Workshop_Name__c', '').strip()
            primary_category = row.get('Category__c', '').strip()
            secondary_category = row.get('Secondary_Category__c', '').strip()
            short_description = row.get('Short_Description__c', '').strip()
            full_description = row.get('Description__c', '').strip()
            level = row.get('Difficulty_Level__c', '').strip().lower()
            prerequisite_workshops_raw = row.get('Prerequisite_Workshops__c', '').strip()
            prerequisites_description = row.get('Prerequisites__c', '').strip()
            duration_min = row.get('Duration_min__c', '').strip()
            software_requirements = row.get('Software_Requirements__c', '').strip()
            cloud_option = row.get('Cloud_option__c', '').strip()
            materials_url = row.get('dlab_Workshop_Materials_text__c', '').strip()
            before_you_join = ''  # No before_you_join column available
            
            # Map categories
            primary_cat_mapped = category_map.get(primary_category, 'other')
            
            # Handle category - can be string or array
            if secondary_category:
                secondary_cat_mapped = category_map.get(secondary_category, '')
                if secondary_cat_mapped and secondary_cat_mapped != primary_cat_mapped:
                    category = [primary_cat_mapped, secondary_cat_mapped]
                else:
                    category = primary_cat_mapped
            else:
                category = primary_cat_mapped
            
            # Use materials URL from sheet or generate GitHub URL
            if materials_url:
                github_url = materials_url
            else:
                repo_name = title_to_github_repo(title)
                github_url = f'https://github.com/dlab-berkeley/{repo_name}'
            
            # Parse prerequisite workshops for cards (semicolon-separated)
            prerequisites = []
            if prerequisite_workshops_raw:
                # Split by semicolon and clean up each prerequisite
                prerequisites = [prereq.strip() for prereq in prerequisite_workshops_raw.split(';') if prereq.strip()]
            
            # Handle duration
            if duration_min:
                try:
                    duration_num = int(duration_min)
                    duration = f'{duration_num} minutes'
                except (ValueError, TypeError):
                    # Fallback to default pattern-based duration
                    if 'Parts' in title or 'parts' in title.lower():
                        duration = '120 minutes'
                    else:
                        duration = '90 minutes'
            else:
                # Fallback to default pattern-based duration
                if 'Parts' in title or 'parts' in title.lower():
                    duration = '120 minutes'
                else:
                    duration = '90 minutes'
            
            # Create workshop entry
            workshop = {
                'title': title,
                'category': category,
                'level': level,
                'description': short_description,
                'github_url': github_url,
                'prerequisites': prerequisites,
                'duration': duration
            }
            
            # Add optional fields if they exist
            if software_requirements:
                workshop['software_requirements'] = software_requirements
            if cloud_option:
                workshop['cloud_option'] = cloud_option
            if before_you_join:
                workshop['before_you_join'] = before_you_join
            if prerequisites_description:
                workshop['prerequisites_description'] = prerequisites_description
            if full_description:
                workshop['full_description'] = full_description
            
            workshops.append(workshop)
            
        except Exception as e:
            print(f"Error parsing workshop row: {e}")
            print(f"Row data: {row}")
            continue
    
    # Sort by title for consistency
    workshops.sort(key=lambda x: x['title'])
    
    return workshops

def update_workshops_yaml(workshops: List[Dict], output_path: Path):
    """
    Update the workshops.yml file with new data
    """
    # Create the YAML structure
    data = {
        'workshops': workshops
    }
    
    # Add header comment
    header = f"""# D-Lab Workshops Data File
# Generated from Google Sheets
# Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# DO NOT EDIT MANUALLY - This file is automatically generated from Google Sheets

"""
    
    # Create directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write YAML file with custom formatting
    with open(output_path, 'w') as f:
        f.write(header)
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True, 
                 default_style=None, width=float('inf'))
    
    print(f"Updated {output_path} with {len(workshops)} workshops")

def main():
    """
    Main function to fetch and update workshop catalog data
    """
    # Get environment variables
    sheet_id = os.environ.get('GOOGLE_WORKSHOPS_SHEET_ID')
    
    if not sheet_id:
        print("Error: GOOGLE_WORKSHOPS_SHEET_ID environment variable not set")
        print("Please set it to your Google Sheet ID for the workshop catalog")
        sys.exit(1)
    
    # Define paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    output_path = project_root / '_data' / 'workshops.yml'
    
    print(f"Fetching workshop catalog from Google Sheet: {sheet_id}")
    
    # Fetch data
    raw_data = fetch_google_sheet_data(sheet_id)
    
    if not raw_data:
        print("No data fetched from Google Sheet")
        return
    
    print(f"Fetched {len(raw_data)} rows from Google Sheet")
    
    # Parse and transform data
    workshops = parse_workshop_catalog(raw_data)
    
    print(f"Parsed {len(workshops)} workshops")
    
    # Update YAML file
    update_workshops_yaml(workshops, output_path)
    
    print("Successfully updated workshop catalog data")

if __name__ == "__main__":
    main()