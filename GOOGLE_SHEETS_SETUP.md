# Google Sheets Integration Setup

This document explains how to set up and use the Google Sheets integration for displaying active workshops on the D-Lab workshops website.

## Overview

The website automatically fetches data from a Google Sheet daily to display currently active workshops with registration information. Active workshops are highlighted in the catalog and sorted to appear first.

## Google Sheet Format

Your Google Sheet should have the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| title | Workshop title (must match catalog) | Python Fundamentals: Parts 1-3 |
| date | Workshop date (MM/DD/YYYY) | 12/15/2025 |
| time | Workshop time (HH:MM AM/PM) | 2:00 PM |
| registration_url | Link to registration | https://berkeley.zoom.us/meeting/register/... |
| instructor | Instructor name | Jane Doe |
| location | Workshop location | Online |
| description | Optional description | Learn Python basics in this 3-part series |

## Setup Instructions

### 1. Create Your Google Sheet

1. Create a new Google Sheet with the columns listed above
2. Make the sheet publicly readable:
   - Click "Share" button
   - Click "Change to anyone with the link"
   - Set permission to "Viewer"
   - Copy the sharing link

### 2. Get Your Sheet ID

From the Google Sheets URL:
```
https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE/edit#gid=0
```

The Sheet ID is the part between `/d/` and `/edit`.

### 3. Configure GitHub Repository

1. Go to your repository Settings → Secrets and variables → Actions
2. Add a new repository secret:
   - Name: `GOOGLE_SHEET_ID`
   - Value: Your Google Sheet ID

### 4. Enable GitHub Actions

The workflow will run automatically:
- Daily at 8 AM UTC (1 AM PST)
- Can be triggered manually from Actions tab

## How It Works

1. **Data Fetching**: The Python script fetches data from your Google Sheet
2. **Data Processing**: Workshops are parsed and sorted by date
3. **JSON Update**: The `_data/upcoming_workshops.json` file is updated
4. **Website Display**: JavaScript dynamically updates workshop cards to show:
   - Green border highlight for active workshops
   - "Next session" badge with date
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

1. **Check title matching**: Workshop titles in the Google Sheet must exactly match those in `_data/workshops.yml`
2. **Check date format**: Dates must be in MM/DD/YYYY format
3. **Check GitHub Actions**: Ensure the workflow is running successfully

### Manual Update

To manually trigger an update:
1. Go to Actions tab in GitHub
2. Select "Update Workshop Data from Google Sheets"
3. Click "Run workflow"

## Maintenance

- The Google Sheet should be updated with new workshop sessions as they're scheduled
- Remove past workshops to keep the sheet clean
- The website automatically updates daily, no manual intervention needed