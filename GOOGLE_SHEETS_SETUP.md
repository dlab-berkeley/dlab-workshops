# Google Sheets Integration Setup

This document explains how to set up and use the Google Sheets integration for displaying active workshops on the D-Lab workshops website.

## Overview

The website automatically fetches data from a Google Sheet daily to display currently active workshops with registration information. Active workshops are highlighted in the catalog and sorted to appear first. This integration uses Google Cloud service account authentication for secure access.

## Google Sheet Format (Salesforce Export)

The system is configured to parse Salesforce event export format with these columns:

| Column | Description | Example |
|--------|-------------|---------|
| evsprk__Event_Title__c | Workshop title | Python Fundamentals: Parts 1-3 |
| evsprk__Start_Date__c | Workshop date (YYYY-MM-DD) | 2025-08-19 |
| evsprk__Stage__c | Workshop status (must be "Active") | Active |
| evsprk__Event_Homepage_Link__c | HTML link with registration URL | `<a href="https://..." target="_blank">Open Event Home Page</a>` |

## Setup Instructions

### 1. Set Up Google Cloud Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Enable Google Sheets API:
   - Go to "APIs & Services" → "Library"
   - Search for "Google Sheets API"
   - Click "Enable"
4. Create Service Account:
   - Go to "IAM & Admin" → "Service Accounts"
   - Click "+ CREATE SERVICE ACCOUNT"
   - Name: `dlab-workshop-reader`
   - Create and download JSON key

### 2. Share Your Google Sheet

1. Get the service account email from the JSON key (e.g., `dlab-workshop-reader@project-id.iam.gserviceaccount.com`)
2. Share your Google Sheet with this email as "Viewer"
3. Note your Sheet ID from the URL:
   ```
   https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE/edit#gid=0
   ```

### 3. Configure GitHub Repository

1. Go to your repository Settings → Secrets and variables → Actions
2. Add two repository secrets:
   - **GOOGLE_SHEET_ID**: Your Google Sheet ID
   - **GOOGLE_SERVICE_ACCOUNT_KEY**: The entire JSON key file contents

### 4. Automation Schedule

The workflow runs automatically:
- Daily at 8 AM UTC (1 AM PST)
- Can be triggered manually from Actions tab

## How It Works

1. **Service Account Authentication**: GitHub Actions uses the service account credentials to securely access your private Google Sheet
2. **Data Fetching**: The Python script fetches data using Google Sheets API
3. **Data Processing**: 
   - Filters for workshops with `evsprk__Stage__c = "Active"`
   - Parses Salesforce date format (YYYY-MM-DD)
   - Extracts registration URL from HTML anchor tags
4. **JSON Update**: The `_data/upcoming_workshops.json` file is updated
5. **Website Display**: JavaScript dynamically updates workshop cards to show:
   - Green border highlight for active workshops
   - "Available Now" badge
   - Register button linking to registration URL
   - Active workshops sorted first in category pages

## Features

### Workshop Highlighting
Active workshops get:
- Green border and shadow
- Session date badge
- Registration button

### Sorting
Workshop lists show:
- "Currently Available" section first
- "Workshop Catalog" section for inactive workshops

### Available Now Page
A dedicated page (`/available-now`) shows only active workshops with:
- Full schedule table
- Registration links
- Session details

## Troubleshooting

### Workshops Not Showing as Active

1. **Check column names**: Ensure your sheet has the Salesforce export columns (`evsprk__Event_Title__c`, etc.)
2. **Check workshop status**: Only workshops with `evsprk__Stage__c = "Active"` are included
3. **Check service account sharing**: Verify the sheet is shared with your service account email
4. **Check GitHub Actions logs**: Look for errors in the Actions tab

### Title Matching

The system uses case-insensitive fuzzy matching to connect sheet workshops with catalog entries:
- "PYTHON FUNDAMENTALS: PARTS 1-3" matches "Python Fundamentals: Parts 1-3"
- "R FUNDAMENTALS: PARTS 1-4" matches "R Fundamentals: Parts 1-4"

### Manual Update

To manually trigger an update:
1. Go to Actions tab in GitHub
2. Select "Update Workshop Data from Google Sheets"
3. Click "Run workflow"

## Security Notes

- The Google Sheet remains private - only accessible by the service account
- Service account has read-only access
- Credentials are stored encrypted in GitHub Secrets
- No sensitive data is exposed in the public repository