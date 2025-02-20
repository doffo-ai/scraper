from database_creation import scrape_funda_listings

BASE_URL = "https://www.funda.nl/zoeken/koop?selected_area=[%22provincie-zuid-holland%22,%22provincie-noord-holland%22,%22utrecht%22]&price=%22175000-225000%22&publication_date=%221%22&availability=[%22available%22,%22negotiations%22,%22unavailable%22]"

if __name__ == "__main__":
    scrape_funda_listings(BASE_URL) 