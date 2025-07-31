#!/usr/bin/env python3
"""
Test script to verify Google Sheets connection
"""

import json
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import our module
sys.path.insert(0, str(Path(__file__).parent))

from fetch_google_sheets import get_google_sheets_service, fetch_google_sheet_data

def test_connection():
    """Test the Google Sheets connection"""
    
    # Check if credentials are set
    if not os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY'):
        print("❌ GOOGLE_SERVICE_ACCOUNT_KEY environment variable not set")
        print("\nTo test locally, run:")
        print("export GOOGLE_SERVICE_ACCOUNT_KEY='<paste your JSON key here>'")
        print("export GOOGLE_SHEET_ID='<your sheet ID>'")
        return False
    
    if not os.environ.get('GOOGLE_SHEET_ID'):
        print("❌ GOOGLE_SHEET_ID environment variable not set")
        return False
    
    print("✅ Environment variables found")
    
    # Test service creation
    print("\n📋 Testing Google Sheets service creation...")
    service = get_google_sheets_service()
    if service:
        print("✅ Successfully created Google Sheets service")
    else:
        print("❌ Failed to create Google Sheets service")
        return False
    
    # Test fetching data
    print("\n📊 Testing data fetch...")
    sheet_id = os.environ.get('GOOGLE_SHEET_ID')
    data = fetch_google_sheet_data(sheet_id)
    
    if data:
        print(f"✅ Successfully fetched {len(data)} rows from the sheet")
        print("\n📝 First row of data:")
        print(json.dumps(data[0], indent=2))
    else:
        print("❌ No data fetched - check if:")
        print("   1. The sheet is shared with: dlab-workshop-reader@dlab-admin.iam.gserviceaccount.com")
        print("   2. The sheet ID is correct")
        print("   3. The sheet has data in it")
        return False
    
    return True

if __name__ == "__main__":
    print("🔧 Google Sheets Connection Test")
    print("=" * 40)
    
    if test_connection():
        print("\n✅ All tests passed! Your connection is working.")
    else:
        print("\n❌ Connection test failed. Please check the errors above.")