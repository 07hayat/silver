import requests
from bs4 import BeautifulSoup
from functions import log

def get_new_listings(client):
    """
    Fetch scheduled new listings from Binance announcements.
    """
    try:
        url = "https://www.binance.com/en/support/announcement"
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a", href=True)

        new_listings = []
        for link in links:
            if "will list" in link.text.lower() or "new listing" in link.text.lower():
                log(f"Announcement found: {link.text}")
                # Extract symbol based on announcement patterns
                symbol = extract_symbol_from_text(link.text)
                if symbol:
                    new_listings.append(symbol)

        # Validate symbols with Binance API
        valid_symbols = validate_symbols(client, new_listings)
        log(f"Validated Scheduled New Listings: {valid_symbols}")
        return valid_symbols
    except Exception as e:
        log(f"Error fetching new listings: {e}")
        return []

def extract_symbol_from_text(text):
    """
    Extract symbols for scheduled new listings from announcement text.
    """
    try:
        if "USDT" in text:
            # Look for patterns like "Binance Will List XYZ/USDT"
            return text.split()[2].replace("/", "")
    except Exception as e:
        log(f"Error extracting symbol from text: {e}")
    return None

def validate_symbols(client, symbols):
    """
    Validate symbols against Binance's active trading pairs.
    """
    try:
        exchange_info = client.get_exchange_info()
        valid_symbols = [s['symbol'] for s in exchange_info['symbols'] if s['status'] == 'TRADING']
        return [symbol for symbol in symbols if symbol in valid_symbols]
    except Exception as e:
        log(f"Error validating symbols: {e}")
        return []

def detect_real_time_new_listings(current_symbols, previous_symbols):
    """
    Detect newly added trading pairs by comparing current and previous symbols.
    """
    return [symbol for symbol in current_symbols if symbol not in previous_symbols]
