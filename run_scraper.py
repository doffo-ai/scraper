import json
from datetime import datetime
import time
from nav_page_extract import extract_listing_links
from page_extract import get_house_features
import logging

FUNDA_URL = "https://www.funda.nl/zoeken/koop?selected_area=[%22provincie-zuid-holland%22,%22provincie-noord-holland%22,%22utrecht%22]&price=%22175000-225000%22&publication_date=%221%22&availability=[%22available%22,%22negotiations%22,%22unavailable%22]"

# Setup logging
logging.basicConfig(
    filename='scraper.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def load_database():
    try:
        with open('database.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def update_database():
    start_msg = f"Starting update at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    print(f"\n{start_msg}")
    logging.info(start_msg)
    
    database = load_database()
    existing_addresses = {entry['features']['address'] for entry in database if entry['features'].get('address')}
    new_entries = []
    
    try:
        if listings := extract_listing_links(FUNDA_URL):
            msg = f"Found {len(listings)} listings to check"
            print(msg)
            logging.info(msg)
            
            for listing_url in listings:
                if result := get_house_features(listing_url):
                    if result['features']['address'] not in existing_addresses:
                        new_entries.append(result)
                        msg = f"Added new listing: {result['features']['address']}"
                        print(msg)
                        logging.info(msg)
                time.sleep(5)
            
            if new_entries:
                database.extend(new_entries)
                
                unique_entries = {}
                for entry in database:
                    if address := entry['features'].get('address'):
                        if (address not in unique_entries or 
                            entry['features']['extraction_timestamp'] > 
                            unique_entries[address]['features']['extraction_timestamp']):
                            unique_entries[address] = entry
                
                cleaned_database = list(unique_entries.values())
                msg = f"Removed duplicates. Database size: {len(database)} → {len(cleaned_database)}"
                print(f"\n{msg}")
                logging.info(msg)
                
                with open('database.json', 'w') as f:
                    json.dump(cleaned_database, f, indent=2)
                
                msg = f"Added {len(new_entries)} new listings to database"
                print(msg)
                logging.info(msg)
            else:
                msg = "No new listings found"
                print(msg)
                logging.info(msg)
    except Exception as e:
        error_msg = f"Error during update: {e}"
        print(error_msg)
        logging.error(error_msg)
        raise

if __name__ == "__main__":
    update_database() 