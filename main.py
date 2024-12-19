import os
import json
from functions import POSITIONS_FILE
import time
from functions import get_account_balance, place_market_order, fetch_24hr_volume
from config import BINANCE_API_KEY, BINANCE_API_SECRET
from binance.client import Client
from utils import log
from trade_logic import execute_daily_trading
from trade_logic import execute_daily_trading, dynamic_profit_capture


PREVIOUS_PAIRS_FILE = "previous_trading_pairs.json"

NEW_LISTING_PROFIT_TARGET = 10  # 1000% gain (10x)
API_CALL_INTERVAL = 1  # Time in seconds to wait between API calls


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

def detect_new_listings(client, current_pairs):
    """Detect newly listed symbols by comparing with saved pairs."""
    log("Checking for new listings...")
    previous_pairs = load_previous_trading_pairs()
    new_pairs = [pair for pair in current_pairs if pair not in previous_pairs]

    if new_pairs:
        log(f"Newly listed pairs detected: {new_pairs}")
        save_trading_pairs(current_pairs)  # Update the file with current pairs
        return new_pairs
    
    log("No new listings detected.")
    return []

def handle_new_listing(client, new_pairs):
    """Handle trading for newly listed symbols."""
    for symbol in new_pairs:
        log(f"Processing new listing: {symbol}")
        usdt_balance = get_account_balance(client, "USDT")

        if usdt_balance < 100:
            log("Insufficient USDT balance to trade new listings.")
            continue

        # Sell 100-200 USDT worth of existing assets
        # This is a placeholder for logic to select and sell existing coins
        log("Selling 100-200 USDT worth of existing coins to fund new listing trade.")
        # Add code to sell assets here

        # Buy the new listing
        log(f"Placing buy order for {symbol}.")
        # WARNING: Uncomment the next line to place real orders
        # place_market_order(client, symbol, "BUY", usdt_balance // len(new_pairs))
        time.sleep(API_CALL_INTERVAL)  # Respect API rate limits

def daily_trading(client):
    """Perform daily trading activities like volume spike or top gainer trading."""
    log("Executing daily trading strategies...")
    # Add volume spike and top gainer logic here
    # Placeholder for daily trading activities
    time.sleep(API_CALL_INTERVAL)  # Respect API rate limits
from trade_logic import dynamic_profit_capture

def monitor_positions(client):
    """Monitor all positions in positions.json for trailing stop conditions."""
    try:
        if not os.path.exists(POSITIONS_FILE):
            log("No positions file found. Skipping position monitoring.")
            return

        with open(POSITIONS_FILE, "r") as f:
            positions = json.load(f)

        # Monitor each position except USDT
        for symbol, details in positions.items():
            if symbol == "USDT":  # Skip USDT
                log("Skipping USDT. Not a tradeable symbol.")
                continue

            entry_price = details["entry_price"]
            quantity = details["quantity"]
            log(f"Monitoring {symbol} for trailing stop. Entry Price: {entry_price}, Quantity: {quantity}")

            # Start trailing stop monitoring
            if quantity > 0:
                dynamic_profit_capture(client, symbol, entry_price, trailing_percent=2)

    except Exception as e:
        log(f"Error during position monitoring: {e}")

import time

def main():
    log("Starting trading bot...")
    try:
        client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
    except Exception as e:
        log(f"Error initializing Binance client: {e}")
        return

    while True:
        try:
            # Monitor existing positions
            monitor_positions(client)

            # Execute daily trading strategies
            log("Executing daily trading strategies...")
            execute_daily_trading(client)

            # Fetch all current trading pairs
            try:
                exchange_info = client.get_exchange_info()
                current_symbols = [symbol["symbol"] for symbol in exchange_info["symbols"]]
                time.sleep(API_CALL_INTERVAL)  # Respect API rate limits
            except Exception as e:
                log(f"Error fetching exchange info: {e}")

            # Detect and handle new listings
            new_pairs = detect_new_listings(client, current_symbols)
            if new_pairs:
                handle_new_listing(client, new_pairs)

            # Perform additional trading strategies
            daily_trading(client)

            # Sleep before the next cycle
            log("Sleeping for 1 minute before the next cycle...")
            time.sleep(60)  # Adjust interval as needed

        except KeyboardInterrupt:
            log("Bot stopped manually.")
            break
        except Exception as e:
            log(f"Unexpected error in main loop: {e}")
            time.sleep(10)  # Small delay before retrying

if __name__ == "__main__":
    main()

