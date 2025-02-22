from src.utils import get_project_root
import requests
import json
import logging
import os

# Create logs directory if it doesn't exist
logs_dir = os.path.join(get_project_root(), 'logs')
os.makedirs(logs_dir, exist_ok=True)

# Setup logging
log_file = os.path.join(logs_dir, 'fetch.log')
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

def fetch_latest_database(owner, repo, path='database.json'):
    """Fetch the latest database.json from GitHub repository"""
    try:
        url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/{path}"
        print(f"Fetching from URL: {url}")
        
        response = requests.get(url)
        print(f"Response status: {response.status_code}")
        response.raise_for_status()
        
        database = json.loads(response.text)
        
        data_dir = os.path.join(get_project_root(), 'data')
        os.makedirs(data_dir, exist_ok=True)
        output_file = os.path.join(data_dir, 'downloaded_database.json')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(database, f, indent=2)
            
        msg = f"Successfully fetched and saved database to {output_file}"
        print(msg)
        logging.info(msg)
        
        return database
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(error_msg)
        logging.error(error_msg)
        return None

if __name__ == "__main__":
    database = fetch_latest_database("doffo-ai", "scraper")
    
    if database:
        print(f"Successfully fetched database with {len(database)} entries")
    else:
        print("Failed to fetch database") 