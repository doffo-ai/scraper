import requests
from bs4 import BeautifulSoup
from .utils import make_request
from ..utils import get_project_root
import os

def load_zipcodes(filename=None):
    """Load valid postal codes from a file"""
    if filename is None:
        filename = os.path.join(get_project_root(), 'data', 'zipcodes.txt')
    try:
        with open(filename, 'r') as f:
            # Remove brackets, quotes, and spaces, then split by commas
            content = f.read().strip('[]').replace("'", "").replace(" ", "")
            return {code.strip() for code in content.split(',') if code.strip()}
    except FileNotFoundError:
        print(f"Warning: {filename} not found")
        return set()

def extract_listing_links(url):
    """Extract listing links from a Funda search page, but only for relevant postal codes
    Returns:
        list: A list of URLs for listings in relevant postal codes
    """
    valid_zipcodes = load_zipcodes()
    
    if html := make_request(url):
        soup = BeautifulSoup(html, 'html.parser')
        return [
            f"https://www.funda.nl{link['href']}"
            for link in soup.find_all('a', href=lambda x: x and '/detail/koop/' in x)
            if (div := link.find('div', class_='truncate text-neutral-80'))
            and div.text.strip()[:4].isdigit()
            and div.text.strip()[:4] in valid_zipcodes
        ]
    return []

if __name__ == '__main__':
    url = "https://www.funda.nl/zoeken/koop?selected_area=[%22groningen%22]"
    urls = extract_listing_links(url)
    
    if urls:
        for url in urls:
            print(url)
    else:
        print("No results to process")