import requests

def make_request(url):
    try:
        response = requests.get(
            url, 
            headers={'User-Agent': 'Mozilla/5.0'}, 
            timeout=10
        )
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Request failed for {url}: {e}")
        return None 