# GLEARN CBC Data

This repository hosts the **Curriculum-Based Competency (CBC) aligned learning data** for GLEARN.  
It syncs automatically from the official Google Sheet to JSON, which is published via GitHub Pages.

## Structure
- `package.json` → Node setup for the sync script
- `scripts/sync.mjs` → Script to fetch Google Sheet CSV and convert to JSON
- `.github/workflows/sync.yml` → GitHub Action to auto-sync every 24 hours
- `docs/entries.json` → Published JSON file with all CBC-aligned Q&A

## Data Source
Data is pulled from:  
[Google Sheet CSV](https://docs.google.com/spreadsheets/d/e/2PACX-1vShg3fcpczXeWIQxo7VJ2bNbJYqyUOP00mOojU1W7tMGiZJqyeIigd-9S5cX24ZMX5qlV_FnKSIjFSU/pub?output=csv)

## Output
Latest JSON is always available here (auto-updated):  
👉 https://jgkiende.github.io/glearn-cbc-data/entries.json

## License
This repository is currently for internal/prototype use.  
