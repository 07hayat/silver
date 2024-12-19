import os
import json
from functions import get_account_balance, place_market_order, fetch_24hr_volume
from config import BINANCE_API_KEY, BINANCE_API_SECRET
from binance.client import Client
from utils import log

PREVIOUS_PAIRS_FILE = "previous_trading_pairs.json"


def load_previous_trading_pairs():
    """Load previously known trading pairs from file."""
    try:
        if not os.path.exists(PREVIOUS_PAIRS_FILE) or os.path.getsize(PREVIOUS_PAIRS_FILE) == 0:
            log(f"Previous trading pairs file is missing or empty. Initializing new file.")
            save_trading_pairs([])  # Initialize with an empty list
            return []

        with open(PREVIOUS_PAIRS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        log(f"Error decoding JSON from {PREVIOUS_PAIRS_FILE}. Reinitializing file.")
        save_trading_pairs([])  # Reinitialize with an empty list
        return []
    except Exception as e:
        log(f"Unexpected error loading previous trading pairs: {e}")
        return []

def save_trading_pairs(pairs):
    """Save trading pairs to file."""
    try:
        with open(PREVIOUS_PAIRS_FILE, "w") as f:
            json.dump(pairs, f)
        log(f"Trading pairs successfully saved.")
    except Exception as e:
        log(f"Error saving trading pairs: {e}")

def mock_fetch_current_price(client, symbol):
    """Simulate fetching the current live price."""
    mock_prices = {
        "BTCUSDT": 101900.67,
        "ETHUSDT": 1900.00,
        "DOGEUSDT": 0.25
    }
    return mock_prices.get(symbol, 0.0)

def test_new_listings_detection():
    """Test detecting new listings."""
    log("Testing new listings detection...")
    previous_pairs = load_previous_trading_pairs()
    current_pairs = ["BTCUSDT", "ETHUSDT", "DOGEUSDT"]  # Simulated current pairs
    new_pairs = [pair for pair in current_pairs if pair not in previous_pairs]

    if new_pairs:
        log(f"New listings detected: {new_pairs}")
        save_trading_pairs(current_pairs)  # Update the file with current pairs
    else:
        log("No new listings detected.")

def test_profit_taking():
    """Simulate a profit-taking condition."""
    log("Testing profit-taking logic...")
    symbol = "BTCUSDT"
    current_price = 150000.00  # Simulated price
    target_price = 120000.00  # Profit-taking target
    if current_price >= target_price:
        log(f"Profit target reached for {symbol}. Current price: {current_price}")
    else:
        log(f"Profit target not yet reached for {symbol}. Current price: {current_price}")

def test_api_error_handling():
    """Simulate API error handling."""
    log("Testing API error handling...")
    try:
        raise Exception("Simulated API failure.")
    except Exception as e:
        log(f"Handled API error: {e}")

def select_and_sell_assets(client, usdt_needed):
    """Select and sell assets to fund new listings."""
    log(f"Attempting to free up {usdt_needed} USDT for new listings.")
    account_balances = client.get_account()["balances"]
    sold_usdt = 0

    for balance in account_balances:
        asset = balance["asset"]
        free_balance = float(balance["free"])
        if asset != "USDT" and free_balance > 0:
            symbol = f"{asset}USDT"
            price = mock_fetch_current_price(client, symbol)
            usdt_value = free_balance * price

            if usdt_value >= usdt_needed - sold_usdt:
                sell_quantity = (usdt_needed - sold_usdt) / price
                log(f"Selling {sell_quantity} of {asset} for approximately {usdt_needed - sold_usdt} USDT.")
                # Uncomment to place real orders
                # place_market_order(client, symbol, "SELL", sell_quantity)
                sold_usdt += usdt_value
                break

            else:
                log(f"Selling all {free_balance} of {asset} for approximately {usdt_value} USDT.")
                # Uncomment to place real orders
                # place_market_order(client, symbol, "SELL", free_balance)
                sold_usdt += usdt_value

    if sold_usdt >= usdt_needed:
        log(f"Successfully freed up {sold_usdt} USDT for new listings.")
    else:
        log(f"Failed to free up enough USDT. Only managed {sold_usdt} USDT.")

def trade_top_gainers(client):
    """Simulate trading top gainers."""
    log("Trading top gainers...")
    top_gainers = ["BTCUSDT", "ETHUSDT"]  # Simulated top gainers

    for symbol in top_gainers:
        price = mock_fetch_current_price(client, symbol)
        log(f"Top gainer detected: {symbol} at price {price}. Considering trade...")
        # Example: Uncomment to place trades
        # place_market_order(client, symbol, "BUY", 0.001)

def edge_tests():
    """Run edge tests to validate trading logic."""
    log("Starting Edge Tests...")

    # Initialize Binance client
    client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

    # Test fetching account balance
    log("Testing account balance fetching...")
    usdt_balance = get_account_balance(client, "USDT")
    log(f"USDT Balance: {usdt_balance}")

    # Test fetching 24-hour volume for a pair
    log("Testing 24-hour volume fetching...")
    volume_data = fetch_24hr_volume(client, "BTCUSDT")
    if volume_data:
        log(f"Volume Data for BTCUSDT: {volume_data}")
    else:
        log("Failed to fetch volume data for BTCUSDT.")

    # Test placing a market order (simulation)
    log("Testing market order placement...")
    # WARNING: Uncomment the next lines only if you want to place a real order.
    # result = place_market_order(client, "BTCUSDT", "BUY", 0.001)
    # log(f"Market Order Result: {result}")

    # Test new listing detection
    log("Testing new listing detection...")
    test_new_listings_detection()

    # Test profit-taking logic
    log("Testing profit-taking logic...")
    test_profit_taking()

    # Test API error handling
    log("Testing API error handling...")
    test_api_error_handling()

    # Test selecting and selling assets
    log("Testing selecting and selling assets...")
    select_and_sell_assets(client, 200)

    # Test trading top gainers
    log("Testing trading top gainers...")
    trade_top_gainers(client)

    # Test fetching mock price
    log("Testing mock price fetching...")
    mock_price = mock_fetch_current_price(client, "BTCUSDT")
    log(f"Mocked price for BTCUSDT: {mock_price}")

    log("Edge Tests Completed.")

if __name__ == "__main__":
    edge_tests()
