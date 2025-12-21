"""
Web Scraper for vidange.tn using Selenium WebDriver (Edge)
"""

import os
import time
import logging
import json
import sqlite3
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
from dotenv import load_dotenv


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


class DatabaseManager:
    """Handles SQLite database operations"""
    def __init__(self, db_path: str = 'plates.db'):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    plate TEXT UNIQUE,
                    marque_modele TEXT,
                    carburant TEXT,
                    mise_circulation TEXT,
                    puissance_fiscale TEXT,
                    type TEXT,
                    moteur TEXT,
                    carosserie TEXT,
                    cylindree TEXT
                )
            ''')
            conn.commit()

    def save_result(self, data: dict):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO results (
                        timestamp, plate, marque_modele, carburant, 
                        mise_circulation, puissance_fiscale, type, 
                        moteur, carosserie, cylindree
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data['timestamp'], data['plate'], data['Marque et modèle'],
                    data['Carburant'], data['Mise en circulation'], 
                    data['Puissance Fiscale'], data['Type'], 
                    data['Moteur'], data['Carosserie'], data['Cylindrée']
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"Database error: {e}")


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
        self.implicit_wait = int(os.getenv('IMPLICIT_WAIT', 10))
        self.output_dir = Path(os.getenv('OUTPUT_DIR', 'output'))
        self.output_dir.mkdir(exist_ok=True)
        
        self.db = DatabaseManager()
        self.driver: Optional[webdriver.Edge] = None
        self.data: List[dict] = []
        
        logger.info(f"Scraper initialized for {self.plate_type} plate")
    
    def setup_driver(self) -> webdriver.Edge:
        """Setup and configure Edge WebDriver"""
        logger.info("Setting up Edge WebDriver...")
        
        edge_options = Options()
        if self.headless:
            edge_options.add_argument('--headless')
        
        edge_options.add_argument('--disable-gpu')
        edge_options.add_argument('--no-sandbox')
        edge_options.add_argument('--disable-dev-shm-usage')
        edge_options.add_argument('--disable-blink-features=AutomationControlled')
        edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        edge_options.add_experimental_option('useAutomationExtension', False)
        
        edge_options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
        )
        
        driver_path = Path(__file__).parent / 'msedgedriver.exe'
        if not driver_path.exists():
            raise FileNotFoundError(f"msedgedriver.exe not found at {driver_path}")
            
        service = Service(executable_path=str(driver_path))
        driver = webdriver.Edge(service=service, options=edge_options)
        driver.implicitly_wait(self.implicit_wait)
        driver.maximize_window()
        
        return driver
    
    def save_data(self, filename: Optional[str] = None):
        """Save scraped data to JSON file"""
        if not self.data:
            return
        
        filepath = self.output_dir / (filename if filename else f"scraped_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)
            
        logger.info(f"Data saved to: {filepath}")

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
            
        except Exception as e:
            logger.error(f"Error filling search form: {e}")
            raise

    def scrape_current_page(self) -> Optional[dict]:
        """Extract car details from the current results page"""
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "value"))
            )
            
            required_fields = [
                'Marque et modèle', 'Carburant', 'Mise en circulation', 
                'Puissance Fiscale', 'Type', 'Moteur', 'Carosserie', 'Cylindrée'
            ]
            
            car_details = {
                'timestamp': datetime.now().isoformat(),
                'plate': f"{self.num} TUN {self.serie}" if self.plate_type == 'TUN' else f"RS {self.num_rs}"
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
                return car_details
            return None
            
        except TimeoutException:
            return None

    def run_bulk(self, start_serie: int = 91, end_serie: int = 252):
        """Bulk scrape TUN plates in the given range"""
        try:
            self.driver = self.setup_driver()
            
            for s in range(start_serie, end_serie + 1):
                self.serie = str(s)
                logger.info(f"--- Starting Serie {s} ---")
                
                for n in range(13, 10000):
                    self.num = str(n)
                    self.plate_type = 'TUN'
                    
                    try:
                        self.driver.get(self.target_url)
                        self.fill_search_form()
                        
                        car_data = self.scrape_current_page()
                        if car_data:
                            self.db.save_result(car_data)
                            logger.info(f"Scraped & Saved: {car_data['plate']} -> {car_data.get('Marque et modèle')}")
                            
                    except Exception as e:
                        logger.error(f"Error on {self.num} TUN {self.serie}: {e}")
                        if "no such window" in str(e).lower():
                            self.driver.quit()
                            self.driver = self.setup_driver()
                        continue
                
        finally:
            if self.driver:
                self.driver.quit()

    def run(self):
        """Single search execution method"""
        try:
            self.driver = self.setup_driver()
            self.driver.get(self.target_url)
            self.fill_search_form()
            car_data = self.scrape_current_page()
            if car_data:
                self.db.save_result(car_data)
                logger.info(f"Scraped & Saved: {car_data.get('Marque et modèle')}")
            else:
                logger.warning("No data found.")
        finally:
            if self.driver:
                self.driver.quit()


def main():
    """Main entry point with CLI menu"""
    print("\n" + "="*50)
    print("      VIDANGE.TN PLATE SCRAPER")
    print("="*50)
    
    print("\nChoose Mode:")
    print("1. Single Search (TUN/RS)")
    print("2. Bulk Scrape TUN (91 to 252)")
    
    mode = input("\nEnter choice (1 or 2): ").strip()
    
    if mode == '2':
        print("\n" + "-"*50)
        print("Starting Bulk Scrape (91 TUN 1 to 252 TUN 9999)...")
        print("Results are saved in real-time to 'plates.db'.")
        print("-"*50 + "\n")
        scraper = VidangeScraper()
        scraper.run_bulk(start_serie=91, end_serie=252)
        return

    print("\nChoose Plate Type:")
    print("1. TUN (Standard)")
    print("2. RS (Régime Suspensif)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    plate_type, serie, num, num_rs = 'TUN', '', '', ''
    
    if choice == '2':
        plate_type = 'RS'
        num_rs = input("Enter RS Number: ").strip()
        if not num_rs: return
    else:
        serie = input("Enter Serie (e.g., 153): ").strip()
        num = input("Enter Number (e.g., 3601): ").strip()
        if not serie or not num: return

    scraper = VidangeScraper(plate_type, serie, num, num_rs)
    scraper.run()


if __name__ == "__main__":
    main()
