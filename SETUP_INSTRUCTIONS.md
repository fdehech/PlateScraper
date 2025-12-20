# Instructions for Setting Up Environment Variables

## Quick Setup

1. Open your `.env` file in the PlateScraper folder
2. Update the SERIE and NUM values with your actual search values

Example:
```
# Target website URL
TARGET_URL=https://vidange.tn

# Form input values
SERIE=ABC123
NUM=456789

# Browser settings
HEADLESS=False
IMPLICIT_WAIT=10

# Output settings
OUTPUT_DIR=output
```

## What the Scraper Does Now

1. ✅ Navigates to vidange.tn
2. ✅ Waits for the search form to load
3. ✅ Finds the input field with ID `numSerie` and enters your SERIE value
4. ✅ Finds the input field with ID `numCar` and enters your NUM value
5. ✅ Clicks the search button with class `btn btn-search`
6. ✅ Waits for results to load
7. ✅ Scrapes the results (you can customize what data to extract)
8. ✅ Saves the data to CSV/JSON/Excel

## Running the Scraper

```bash
python scraper.py
```

## Next Steps

After the form is submitted and results appear, you'll need to customize the scraping logic in the `scrape_data()` method to extract the specific data you need from the results page.

Look for the TODO comment in `scraper.py` around line 185 to add your custom result extraction logic.
