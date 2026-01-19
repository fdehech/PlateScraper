# Web Scraper

A Python web scraper built with Selenium WebDriver (Edge) to extract data from vidange*tn.

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

### Run as FastAPI (Recommended)
1. **Start the server**:
   ```bash
   python main.py
   ```
   The API will be available at `http://localhost:8000`.

2. **Scrape via API**:
   - **TUN Plate**: `http://localhost:8000/scrape/tun/{serie}/{num}`
     ```bash
     curl "http://localhost:8000/scrape/tun/153/3601"
     ```
   - **RS Plate**: `http://localhost:8000/scrape/rs/{num_rs}`
     ```bash
     curl "http://localhost:8000/scrape/rs/12345"
     ```

### Run as Script
You can still run the scraper directly for a quick test:
```bash
python scraper.py
```

## Configuration Options

Edit `.env` file to customize:
- `TARGET_URL`: The website to scrape (default: https://vidange.tn)
- `HEADLESS`: Run browser in headless mode (True/False)
- `BROWSER_TYPE`: `chrome` or `edge` (default: `edge`)
- `IMPLICIT_WAIT`: Seconds to wait for elements (default: 10)
- `OUTPUT_DIR`: Directory to save scraped data (default: output)

## Cross-Platform Support (Linux/Ubuntu)

The scraper now supports both **Chrome** and **Edge** and uses `webdriver-manager` to automatically download the correct drivers.

### Setup on Ubuntu VM:
1. **Install Chrome**:
   ```bash
   wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
   sudo apt install ./google-chrome-stable_current_amd64.deb
   ```
2. **Configure `.env`**:
   Set `BROWSER_TYPE=chrome` and `HEADLESS=True` in your `.env` file.

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
