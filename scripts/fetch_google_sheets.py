#!/usr/bin/env python3
"""
Fetch active workshops from Google Sheets and update upcoming_workshops.json
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def get_google_sheets_service():
    """
    Create and return Google Sheets service using service account
    """
    try:
        # Get service account credentials from environment variable
        service_account_info = json.loads(os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY', '{}'))
        
        if not service_account_info:
            raise ValueError("GOOGLE_SERVICE_ACCOUNT_KEY environment variable is not set")
        
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=['https://www.googleapis.com/auth/spreadsheets.readonly']
        )
        
        service = build('sheets', 'v4', credentials=credentials)
        return service
        
    except Exception as e:
        print(f"Error creating Google Sheets service: {e}")
        return None

def fetch_google_sheet_data(sheet_id: str, range_name: str = 'A:Z') -> List[Dict]:
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

def parse_workshop_data(raw_data: List[Dict]) -> List[Dict]:
    """
    Parse and transform raw Google Sheets data into workshop format
    Expected columns from Salesforce export:
    - evsprk__Event_Title__c: Workshop title
    - evsprk__Start_Date__c: Start date (YYYY-MM-DD)
    - evsprk__Event_Homepage_Link__c: HTML link containing registration URL
    """
    workshops = []
    
    for row in raw_data:
        try:
            # Skip empty rows or inactive workshops
            if not row.get('evsprk__Event_Title__c') or row.get('evsprk__Stage__c') != 'Active':
                continue
            
            # Get workshop title
            title = row.get('evsprk__Event_Title__c', '').strip()
            
            # Parse date (format: YYYY-MM-DD)
            date_str = row.get('evsprk__Start_Date__c', '')
            if not date_str:
                continue
            
            # Convert date to datetime (assuming workshops are during business hours)
            workshop_date = datetime.strptime(date_str, "%Y-%m-%d")
            # Set a default time of 9 AM PST (5 PM UTC)
            workshop_datetime = workshop_date.replace(hour=17, minute=0, tzinfo=timezone.utc)
            
            # Extract registration URL from HTML link
            registration_url = ''
            homepage_link = row.get('evsprk__Event_Homepage_Link__c', '')
            if homepage_link:
                # Extract URL from HTML anchor tag
                import re
                url_match = re.search(r'href="([^"]+)"', homepage_link)
                if url_match:
                    registration_url = url_match.group(1)
            
            workshop = {
                'title': title,
                'datetime_iso': workshop_datetime.isoformat(),
                'registration_url': registration_url,
                'date': workshop_date.strftime("%b %d, %Y"),
                'time': 'See event page for details',
                'location': 'Online',
                'instructor': 'D-Lab Staff'
            }
            
            workshops.append(workshop)
            
        except Exception as e:
            print(f"Error parsing workshop row: {e}")
            print(f"Row data: {row}")
            continue
    
    # Sort by date
    workshops.sort(key=lambda x: x['datetime_iso'])
    
    return workshops

def update_upcoming_workshops(workshops: List[Dict], output_path: Path):
    """
    Update the upcoming_workshops.json file
    """
    data = {
        'last_updated': datetime.now(timezone.utc).isoformat(),
        'total_workshops': len(workshops),
        'workshops': workshops
    }
    
    # Create directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write JSON file
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Updated {output_path} with {len(workshops)} workshops")

def main():
    """
    Main function to fetch and update workshop data
    """
    # Get environment variables or use defaults
    sheet_id = os.environ.get('GOOGLE_SHEET_ID')
    
    if not sheet_id:
        print("Error: GOOGLE_SHEET_ID environment variable not set")
        print("Please set it to your Google Sheet ID (the part between /d/ and /edit in the URL)")
        sys.exit(1)
    
    # Define paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    output_path = project_root / '_data' / 'upcoming_workshops.json'
    
    print(f"Fetching data from Google Sheet: {sheet_id}")
    
    # Fetch data
    raw_data = fetch_google_sheet_data(sheet_id)
    
    if not raw_data:
        print("No data fetched from Google Sheet")
        # Still update the file with empty data
        update_upcoming_workshops([], output_path)
        return
    
    print(f"Fetched {len(raw_data)} rows from Google Sheet")
    
    # Parse and transform data
    workshops = parse_workshop_data(raw_data)
    
    # Update JSON file
    update_upcoming_workshops(workshops, output_path)
    
    print("Successfully updated upcoming workshops data")

if __name__ == "__main__":
    main()