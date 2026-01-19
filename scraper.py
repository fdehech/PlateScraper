"""
Web Scraper for vidange.tn using Selenium WebDriver (Edge)
"""

import os
import time
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dotenv import load_dotenv
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from webdriver_manager.chrome import ChromeDriverManager


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
    
    def __init__(self, plate_type: str = 'TUN', serie: str = '', num: str = '', num_rs: str = ''):
        """Initialize the scraper with plate details"""
        load_dotenv()
        
        self.target_url = os.getenv('TARGET_URL', 'https://vidange.tn')
        self.plate_type = plate_type.upper()
        self.serie = serie
        self.num = num
        self.num_rs = num_rs
        
        self.headless = os.getenv('HEADLESS', 'False').lower() == 'true'
        self.browser_type = os.getenv('BROWSER_TYPE', 'edge').lower()
        self.implicit_wait = int(os.getenv('IMPLICIT_WAIT', 10))
        self.output_dir = Path(os.getenv('OUTPUT_DIR', 'output'))
        self.output_dir.mkdir(exist_ok=True)
        
        self.driver: Optional[webdriver.Edge] = None
        self.data: List[Dict] = []
        
        logger.info(f"Scraper initialized for {self.plate_type} plate")
    
    def setup_driver(self) -> webdriver.Remote:
        """Setup and configure WebDriver (Edge or Chrome)"""
        logger.info(f"Setting up {self.browser_type.capitalize()} WebDriver...")
        
        if self.browser_type == 'chrome':
            chrome_options = ChromeOptions()
            if self.headless:
                chrome_options.add_argument('--headless=new')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            
            driver_path = ChromeDriverManager().install()
            service = ChromeService(executable_path=driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            edge_options = EdgeOptions()
            if self.headless:
                edge_options.add_argument('--headless')
            edge_options.add_argument('--disable-gpu')
            edge_options.add_argument('--no-sandbox')
            edge_options.add_argument('--disable-dev-shm-usage')
            edge_options.add_argument('--disable-blink-features=AutomationControlled')
            edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            edge_options.add_experimental_option('useAutomationExtension', False)
            
            driver_path = EdgeChromiumDriverManager().install()
            service = EdgeService(executable_path=driver_path)
            driver = webdriver.Edge(service=service, options=edge_options)

        driver.implicitly_wait(self.implicit_wait)
        driver.maximize_window()
        return driver
    
    def fill_search_form(self):
        """Fill the search form based on plate type and click search"""
        try:
            if self.plate_type == 'RS':
                logger.info("Selecting RS plate type...")
                rs_radio = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.ID, "RSi"))
                )
                self.driver.execute_script("arguments[0].click();", rs_radio)
                time.sleep(1)
                
                num_rs_field = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.ID, "numRS"))
                )
                num_rs_field.clear()
                num_rs_field.send_keys(self.num_rs)
            else:
                num_serie_field = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.ID, "numSerie"))
                )
                num_car_field = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.ID, "numCar"))
                )
                
                num_serie_field.clear()
                num_serie_field.send_keys(self.serie)
                num_car_field.clear()
                num_car_field.send_keys(self.num)
            
            search_button = self.driver.find_element(By.CSS_SELECTOR, "button.btn.btn-search")
            self.driver.execute_script("arguments[0].click();", search_button)
            time.sleep(5)
            
        except Exception as e:
            logger.error(f"Error filling search form: {e}")
            raise
    
    def scrape_data(self):
        """Scrapes car details after form submission"""
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.ID, "numSerie"))
            )
            
            self.fill_search_form()
            
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "value"))
            )
            
            required_fields = [
                'Marque et modèle', 'Carburant', 'Mise en circulation', 
                'Puissance Fiscale', 'Type', 'Moteur', 'Carosserie', 'Cylindrée'
            ]
            
            car_details = {
                'timestamp': datetime.now().isoformat(),
                'plate_type': self.plate_type,
                'serie_searched': self.serie if self.plate_type == 'TUN' else '-',
                'num_searched': self.num if self.plate_type == 'TUN' else self.num_rs
            }
            
            info_elements = self.driver.find_elements(By.XPATH, "//div[div[@class='title'] and div[@class='value']]")
            extracted_data = {}
            
            for element in info_elements:
                title = element.find_element(By.CLASS_NAME, "title").text.strip()
                value = element.find_element(By.CLASS_NAME, "value").text.strip()
                if title:
                    extracted_data[title] = value
            
            for field in required_fields:
                car_details[field] = extracted_data.get(field, '-')
            
            if any(extracted_data.get(f) for f in required_fields):
                self.data.append(car_details)
                logger.info(f"Scraped: {car_details.get('Marque et modèle')}")
            
        except TimeoutException:
            logger.error("Timeout waiting for elements")
            self.driver.save_screenshot(str(self.output_dir / "error_timeout.png"))
            raise
        except Exception as e:
            logger.error(f"Scraping error: {e}")
            raise
    
    def save_data(self):
        """Save scraped data to JSON file"""
        if not self.data:
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = self.output_dir / f'scraped_data_{timestamp}.json'
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)
            
        logger.info(f"Data saved to: {filepath}")
    
    def run(self) -> List[Dict]:
        """Main execution method, returns scraped data"""
        try:
            self.driver = self.setup_driver()
            self.driver.get(self.target_url)
            self.scrape_data()
            # self.save_data() # Optional: keep saving if desired, but return data
            return self.data
        finally:
            if self.driver:
                self.driver.quit()


if __name__ == "__main__":
    # Example usage
    scraper = VidangeScraper(plate_type='TUN', serie='153', num='3601')
    results = scraper.run()
    print(json.dumps(results, indent=4, ensure_ascii=False))
