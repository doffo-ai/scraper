from utils import make_request
from bs4 import BeautifulSoup
from time import sleep
import json
from datetime import datetime
from nav_page_extract import extract_listing_links
from page_extract import get_house_features
import sys

def scrape_funda_listings(base_url, last_page, resume_from=None):
    # Setup
    all_features = []
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"house_features_{timestamp}.json"
    
    # Resume from previous run if specified
    if resume_from:
        try:
            with open(resume_from) as f:
                all_features = json.load(f)
            start_page = (len(all_features) // 15) + 1  # Assume 15 listings per page
            print(f"Resuming from page {start_page} with {len(all_features)} listings")
        except FileNotFoundError:
            start_page = 1
    else:
        start_page = 1

    # Main scraping loop
    for page in range(start_page, last_page + 1):
        try:
            # Get listings from navigation page
            url = f"{base_url}&search_result={page}"
            if listings := extract_listing_links(url):
                print(f"\nPage {page}/{last_page}: Found {len(listings)} listings")
                
                # Extract features from each listing
                for i, listing_url in enumerate(listings, 1):
                    if result := get_house_features(listing_url):
                        all_features.append(result)
                        print(f"Listing {i}: Success")
                    sleep(5)  # Rate limiting
                
                # Save progress
                with open(filename, 'w') as f:
                    json.dump(all_features, f, indent=2)
                print(f"Saved {len(all_features)} total listings")
                
            sleep(2)  # Rate limiting between pages
            
        except Exception as e:
            print(f"Error on page {page}: {e}")
            with open(f"error_log_{timestamp}.txt", 'a') as f:
                f.write(f"Error on page {page}: {str(e)}\n")
    
    print(f"\nCompleted! {len(all_features)} listings saved to {filename}")
    return all_features

if __name__ == "__main__":
    BASE_URL = "https://www.funda.nl/zoeken/koop?selected_area=[%22provincie-zuid-holland%22,%22provincie-noord-holland%22,%22utrecht%22]&price=%22175000-225000%22&availability=[%22available%22,%22negotiations%22,%22unavailable%22]"
    
    try:
        # Simple argument parsing for resume functionality
        resume_file = None
        if '--resume' in sys.argv:
            resume_file = sys.argv[sys.argv.index('--resume') + 1]
        
        scrape_funda_listings(BASE_URL, last_page=276, resume_from=resume_file)
    except KeyboardInterrupt:
        print("\nScraping interrupted. Progress saved.")
    except Exception as e:
        print(f"\nError: {e}")

