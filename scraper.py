"""
Web Scraper for vidange.tn using Selenium WebDriver (Edge)
"""

import os
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from dotenv import load_dotenv
import pandas as pd


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class VidangeScraper:
    """Scraper class for vidange.tn website"""
    
    def __init__(self):
        """Initialize the scraper with environment variables"""
        # Load environment variables
        load_dotenv()
        
        self.target_url = os.getenv('TARGET_URL')
        self.serie = os.getenv('SERIE', '')
        self.num = os.getenv('NUM', '')
        self.headless = os.getenv('HEADLESS', 'False').lower() == 'true'
        self.implicit_wait = int(os.getenv('IMPLICIT_WAIT', 10))
        self.output_dir = Path(os.getenv('OUTPUT_DIR', 'output'))
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(exist_ok=True)
        
        self.driver: Optional[webdriver.Edge] = None
        self.data: List[Dict] = []
        
        logger.info(f"Scraper initialized for URL: {self.target_url}")
    
    def setup_driver(self) -> webdriver.Edge:
        """Setup and configure Edge WebDriver"""
        logger.info("Setting up Edge WebDriver...")
        
        # Configure Edge options
        edge_options = Options()
        
        if self.headless:
            edge_options.add_argument('--headless')
            logger.info("Running in headless mode")
        
        # Additional options for better performance and stability
        edge_options.add_argument('--disable-gpu')
        edge_options.add_argument('--no-sandbox')
        edge_options.add_argument('--disable-dev-shm-usage')
        edge_options.add_argument('--disable-blink-features=AutomationControlled')
        edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        edge_options.add_experimental_option('useAutomationExtension', False)
        
        # Set user agent to avoid detection
        edge_options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
        )
        
        # Use local msedgedriver.exe
        driver_path = Path(__file__).parent / 'msedgedriver.exe'
        
        if driver_path.exists():
            logger.info(f"Using local Edge driver: {driver_path}")
            service = Service(executable_path=str(driver_path))
        else:
            # Fallback to webdriver-manager if local driver not found
            logger.info("Local driver not found, using webdriver-manager...")
            service = Service(EdgeChromiumDriverManager().install())
        
        driver = webdriver.Edge(service=service, options=edge_options)
        
        # Set implicit wait
        driver.implicitly_wait(self.implicit_wait)
        
        # Maximize window
        driver.maximize_window()
        
        logger.info("Edge WebDriver setup complete")
        return driver
    
    def navigate_to_site(self):
        """Navigate to the target website"""
        logger.info(f"Navigating to {self.target_url}...")
        try:
            self.driver.get(self.target_url)
            time.sleep(2)  # Wait for page to load
            logger.info(f"Successfully loaded: {self.driver.title}")
        except Exception as e:
            logger.error(f"Failed to navigate to site: {e}")
            raise
    
    def fill_search_form(self):
        """Fill the search form with SERIE and NUM values and click search"""
        logger.info("Filling search form...")
        
        try:
            # Wait for the form fields to be present
            logger.info("Waiting for numSerie field...")
            num_serie_field = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "numSerie"))
            )
            
            logger.info("Waiting for numCar field...")
            num_car_field = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "numCar"))
            )
            
            # Clear and enter values
            logger.info(f"Entering SERIE value: {self.serie}")
            num_serie_field.clear()
            num_serie_field.send_keys(self.serie)
            time.sleep(0.5)
            
            logger.info(f"Entering NUM value: {self.num}")
            num_car_field.clear()
            num_car_field.send_keys(self.num)
            time.sleep(0.5)
            
            # Find and click the search button
            logger.info("Looking for search button...")
            # Try multiple selectors for the search button
            selectors = [
                "button.btn.btn-search",
                "button.btn-search",
                "//button[contains(text(), 'RECHERCHE')]",
                "//button[contains(@class, 'btn-search')]"
            ]
            
            search_button = None
            for selector in selectors:
                try:
                    if selector.startswith("//"):
                        search_button = self.driver.find_element(By.XPATH, selector)
                    else:
                        search_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if search_button.is_displayed():
                        break
                except:
                    continue
            
            if not search_button:
                raise NoSuchElementException("Could not find search button with any selector")
            
            logger.info("Clicking search button using JavaScript...")
            self.driver.execute_script("arguments[0].click();", search_button)
            
            # Wait for results to load
            time.sleep(5)
            logger.info("Search form submitted")
            
        except Exception as e:
            logger.error(f"Error filling search form: {e}")
            raise
    
    def scrape_data(self):
        """
        Main scraping logic - fills form and then scrapes car details
        """
        logger.info("Starting data scraping...")
        
        try:
            # First, ensure we are on the page and the form is ready
            logger.info("Waiting for page to be ready...")
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "numSerie"))
            )
            
            # Get page title
            logger.info(f"Page title: {self.driver.title}")
            
            # Fill the search form
            self.fill_search_form()
            
            # Now wait for results to appear - looking for the value structure
            logger.info("Waiting for search results to load...")
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "value"))
            )
            
            # Define the specific fields we want to extract
            required_fields = [
                'Marque et modèle', 
                'Carburant', 
                'Mise en circulation', 
                'Puissance Fiscale', 
                'Type', 
                'Moteur', 
                'Carosserie', 
                'Cylindrée'
            ]
            
            # Initialize the result dictionary with metadata
            car_details = {
                'timestamp': datetime.now().isoformat(),
                'serie_searched': self.serie,
                'num_searched': self.num
            }
            
            # Find all info blocks (divs containing title and value)
            info_elements = self.driver.find_elements(By.XPATH, "//div[div[@class='title'] and div[@class='value']]")
            
            extracted_data = {}
            if not info_elements:
                # Fallback: try finding titles and values separately
                titles = self.driver.find_elements(By.CLASS_NAME, "title")
                values = self.driver.find_elements(By.CLASS_NAME, "value")
                
                for t, v in zip(titles, values):
                    key = t.text.strip()
                    val = v.text.strip()
                    if key:
                        extracted_data[key] = val
            else:
                for element in info_elements:
                    try:
                        title = element.find_element(By.CLASS_NAME, "title").text.strip()
                        value = element.find_element(By.CLASS_NAME, "value").text.strip()
                        if title:
                            extracted_data[title] = value
                    except Exception as e:
                        logger.warning(f"Could not extract a specific info block: {e}")
            
            # Map extracted data to our required fields, using '-' as default
            for field in required_fields:
                car_details[field] = extracted_data.get(field, '-')
            
            # Only add to data if we found at least some of the required fields
            if any(extracted_data.get(f) for f in required_fields):
                self.data.append(car_details)
                logger.info(f"Successfully scraped car details for: {car_details.get('Marque et modèle')}")
            else:
                logger.warning("No relevant car details found on the page.")
            
            logger.info(f"Scraped {len(self.data)} items")
            
        except TimeoutException:
            logger.error("Timeout waiting for elements to load")
            screenshot_path = self.output_dir / f"error_timeout_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.driver.save_screenshot(str(screenshot_path))
            logger.info(f"Saved error screenshot to {screenshot_path}")
            raise
        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            raise
    
    def save_data(self, format: str = 'csv'):
        """
        Save scraped data to file
        
        Args:
            format: Output format ('csv', 'json', or 'excel')
        """
        if not self.data:
            logger.warning("No data to save")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            df = pd.DataFrame(self.data)
            
            if format == 'csv':
                filepath = self.output_dir / f'scraped_data_{timestamp}.csv'
                df.to_csv(filepath, index=False, encoding='utf-8-sig')
            elif format == 'json':
                filepath = self.output_dir / f'scraped_data_{timestamp}.json'
                df.to_json(filepath, orient='records', indent=2, force_ascii=False)
            elif format == 'excel':
                filepath = self.output_dir / f'scraped_data_{timestamp}.xlsx'
                df.to_excel(filepath, index=False, engine='openpyxl')
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            logger.info(f"Data saved to: {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            raise
    
    def close(self):
        """Close the browser and cleanup"""
        if self.driver:
            logger.info("Closing browser...")
            self.driver.quit()
            logger.info("Browser closed")
    
    def run(self, save_format: str = 'csv'):
        """
        Main execution method
        
        Args:
            save_format: Format to save data ('csv', 'json', or 'excel')
        """
        try:
            # Setup driver
            self.driver = self.setup_driver()
            
            # Navigate to site
            self.navigate_to_site()
            
            # Scrape data
            self.scrape_data()
            
            # Save data
            self.save_data(format=save_format)
            
            logger.info("Scraping completed successfully!")
            
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            raise
        finally:
            # Always close the browser
            self.close()


def main():
    """Main entry point"""
    logger.info("=" * 50)
    logger.info("Starting Vidange.tn Scraper")
    logger.info("=" * 50)
    
    scraper = VidangeScraper()
    scraper.run(save_format='csv')  # Change to 'json' or 'excel' if needed
    
    logger.info("=" * 50)
    logger.info("Scraper finished")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
