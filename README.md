# Vidange.tn Web Scraper

A Python web scraper built with Selenium WebDriver (Edge) to extract data from vidange.tn.

## Features

- 🌐 **Selenium WebDriver** with Edge browser
- 🔐 **Interactive CLI Menu**: Choose between TUN or RS plates before starting.
- 📝 **Comprehensive Logging**: Console and file-based logs.
- 🛡️ **Anti-detection**: User agents and automation flags.
- 🔄 **Automatic WebDriver Management**: Uses local driver or downloads if needed.

## Prerequisites

- Python 3.8 or higher
- Microsoft Edge browser installed
- Internet connection

## Installation

1. **Navigate to the project directory**
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment variables**
   Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```

## Usage

Run the scraper:
```bash
python scraper.py
```

The scraper will present a menu:
1. Choose **TUN** (Standard) or **RS** (Régime Suspensif).
2. Enter the plate details (Serie/Number for TUN, or RS Number for RS).
3. The browser will start and extract the car details.

## Configuration Options

Edit `.env` file to customize:
- `TARGET_URL`: The website to scrape (default: https://vidange.tn)
- `HEADLESS`: Run browser in headless mode (True/False)
- `IMPLICIT_WAIT`: Seconds to wait for elements (default: 10)
- `OUTPUT_DIR`: Directory to save scraped data (default: output)

## Project Structure

```
PlateScraper/
├── .env                # Environment variables
├── .gitignore          # Git ignore rules
├── requirements.txt    # Python dependencies
├── scraper.py          # Main scraper script
├── README.md           # This file
└── scraper.log         # Log file
```

## License

This project is for educational purposes only. Ensure you have permission to scrape the target website.
