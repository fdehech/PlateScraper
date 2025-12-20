# Vidange.tn Web Scraper

A Python web scraper built with Selenium WebDriver (Edge) to extract data from vidange.tn.

## Features

- 🌐 Selenium WebDriver with Edge browser
- 🔐 Environment-based configuration (URL hidden in `.env`)
- 📊 Multiple export formats (CSV, JSON, Excel)
- 📝 Comprehensive logging
- 🛡️ Anti-detection measures
- 🔄 Automatic WebDriver management

## Prerequisites

- Python 3.8 or higher
- Microsoft Edge browser installed
- Internet connection

## Installation

1. **Clone or navigate to the project directory**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   
   Copy `.env.example` to `.env` and update if needed:
   ```bash
   copy .env.example .env
   ```

   The `.env` file contains:
   ```
   TARGET_URL=https://vidange.tn
   HEADLESS=False
   IMPLICIT_WAIT=10
   OUTPUT_DIR=output
   ```

## Usage

### Basic Usage

Run the scraper:
```bash
python scraper.py
```

### Customization

The scraper is built as a template. You'll need to customize the `scrape_data()` method in `scraper.py` based on what you want to extract from the website.

**Example customization:**
```python
def scrape_data(self):
    # Find all product elements
    products = self.driver.find_elements(By.CSS_SELECTOR, '.product-item')
    
    for product in products:
        data_item = {
            'name': product.find_element(By.CSS_SELECTOR, '.product-name').text,
            'price': product.find_element(By.CSS_SELECTOR, '.product-price').text,
            'description': product.find_element(By.CSS_SELECTOR, '.product-desc').text,
        }
        self.data.append(data_item)
```

### Configuration Options

Edit `.env` file to customize:

- `TARGET_URL`: The website to scrape
- `HEADLESS`: Run browser in headless mode (True/False)
- `IMPLICIT_WAIT`: Seconds to wait for elements (default: 10)
- `OUTPUT_DIR`: Directory to save scraped data (default: output)

### Output Formats

Change the output format in `scraper.py`:
```python
scraper.run(save_format='csv')   # CSV format
scraper.run(save_format='json')  # JSON format
scraper.run(save_format='excel') # Excel format
```

## Project Structure

```
PlateScraper/
├── .env                 # Environment variables (not in git)
├── .env.example         # Example environment file
├── .gitignore          # Git ignore rules
├── requirements.txt    # Python dependencies
├── scraper.py          # Main scraper script
├── README.md           # This file
├── scraper.log         # Log file (generated)
└── output/             # Scraped data output (generated)
```

## Logging

The scraper logs to both console and `scraper.log` file with timestamps and log levels.

## Development

### Adding New Features

1. Modify the `scrape_data()` method for your specific scraping needs
2. Add new methods to the `VidangeScraper` class as needed
3. Update the data structure in `self.data` to match your requirements

### Error Handling

The scraper includes comprehensive error handling:
- Timeout exceptions
- Element not found exceptions
- Navigation errors
- Data saving errors

## Notes

- The scraper uses `webdriver-manager` to automatically download and manage the Edge WebDriver
- Anti-detection measures are included (user agent, automation flags)
- Always respect the website's `robots.txt` and terms of service
- Consider adding delays between requests to avoid overwhelming the server

## Troubleshooting

**Edge WebDriver issues:**
- Ensure Microsoft Edge is installed and up to date
- The webdriver-manager will automatically download the correct driver version

**Element not found:**
- Inspect the website structure and update CSS selectors
- Increase `IMPLICIT_WAIT` in `.env` if elements load slowly

**Permission errors:**
- Run terminal as administrator if needed
- Check that the output directory is writable

## License

This project is for educational purposes only. Ensure you have permission to scrape the target website.
