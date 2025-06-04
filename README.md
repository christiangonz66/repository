# Colorado Job Tracker

A Streamlit application for visualizing job distribution across Colorado cities and counties.

## Features

- Upload CSV files with job location data
- Match locations to Colorado cities using fuzzy matching
- Visualize job distribution by city or county
- Export matched and unmatched data
- Interactive maps and data tables

## Installation

\`\`\`bash
pip install -r requirements.txt
\`\`\`

## Usage

\`\`\`bash
streamlit run app.py
\`\`\`

## Deployment

This app can be deployed to:
- Streamlit Cloud
- Heroku
- Railway
- Any platform supporting Python web applications

## Data Format

Your CSV should contain a column with location information such as:
- City names (e.g., "Denver", "Colorado Springs")
- City, State format (e.g., "Boulder, CO")
- Full addresses containing Colorado cities
