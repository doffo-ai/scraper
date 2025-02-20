from utils import make_request
from bs4 import BeautifulSoup

def generate_page_urls(base_url, last_page):
    return [f"{base_url}&search_result={i}" for i in range(1, last_page + 1)]

def process_navigation_pages(nav_urls, max_pages=None):
    from nav_page_extract import extract_listing_links
    from time import sleep
    
    urls = []
    pages = nav_urls[:max_pages] if max_pages else nav_urls
    
    for i, url in enumerate(pages, 1):
        if listings := extract_listing_links(url):
            urls.extend(listings)
            print(f"Page {i}: Found {len(listings)} listings")
        sleep(2)
    return urls

def extract_house_features(listing_urls, max_listings=None):
    from page_extract import get_house_features
    from time import sleep
    
    features = []
    listings = listing_urls[:max_listings] if max_listings else listing_urls
    
    for i, url in enumerate(listings, 1):
        if result := get_house_features(url):
            features.append(result)
            print(f"Listing {i}: Success")
        sleep(2)
    return features

def get_last_page(base_url):
    if html := make_request(base_url):
        soup = BeautifulSoup(html, 'html.parser')
        # Find pagination elements, return 1 if none found
        pagination = soup.find_all('a', {'role': 'button'})
        if pagination:
            try:
                return max(int(btn.text) for btn in pagination if btn.text.isdigit())
            except ValueError:
                return 1
    return 1

def scrape_funda_listings(base_url, last_page=None, max_pages=None):
    import json
    from datetime import datetime
    import time
    
    if last_page is None:
        last_page = get_last_page(base_url)
        print(f"Found {last_page} pages to scrape")
    
    nav_urls = generate_page_urls(base_url, last_page)[:max_pages]
    all_features = []
    
    for page_num, page_url in enumerate(nav_urls, 1):
        retries = 3
        while retries > 0:
            try:
                print(f"\nProcessing page {page_num}/{len(nav_urls)}:")
                listings = process_navigation_pages([page_url])
                print(f"Extracting features from {len(listings)} listings...")
                all_features.extend(extract_house_features(listings))
                break
            except Exception as e:
                retries -= 1
                if retries == 0:
                    print(f"Failed to process page {page_num} after 3 attempts: {e}")
                else:
                    print(f"Retrying page {page_num} in 5 seconds...")
                    time.sleep(5)
    
    if all_features:
        filename = f"house_features_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(all_features, f, indent=2)
        print(f"\nSaved {len(all_features)} listings to {filename}")
    
    return all_features

if __name__ == "__main__":
    BASE_URL = "https://www.funda.nl/zoeken/koop?selected_area=[%22provincie-zuid-holland%22,%22provincie-noord-holland%22,%22utrecht%22]&price=%22175000-225000%22&availability=[%22available%22,%22negotiations%22,%22unavailable%22]"
    scrape_funda_listings(BASE_URL, 276, max_pages=2)

