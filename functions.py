import os
import json
import logging
import math
from binance.client import Client
from config import BINANCE_API_KEY, BINANCE_API_SECRET, DEBUG_MODE

# Ensure the logs directory exists
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Configure logging to log to both a file and the console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(os.path.join(log_dir, "bot_activity.log")),  # Log to file
        logging.StreamHandler()  # Log to console
    ]
)

def log(message):
    """Log a message to the bot's activity log."""
    logging.info(message)

def get_binance_client():
    """Initialize and return a Binance client."""
    try:
        if DEBUG_MODE == "real":
            log("Initializing Binance client in real mode.")
            return Client(BINANCE_API_KEY, BINANCE_API_SECRET)
        log("Running in simulated mode. No Binance client initialized.")
    except Exception as e:
        log(f"Error initializing Binance client: {e}")
    return None

def get_symbol_info(client, symbol):
    """Fetch symbol info to validate trading pairs and filters."""
    try:
        return client.get_symbol_info(symbol)
    except Exception as e:
        log(f"Error fetching symbol info for {symbol}: {e}")
        return None

def get_account_balance(client, asset):
    """Fetch account balance for a specific asset."""
    try:
        account_info = client.get_account()
        balances = account_info['balances']
        for balance in balances:
            if balance['asset'] == asset:
                return float(balance['free'])
    except Exception as e:
        log(f"Error fetching balance for {asset}: {e}")
    return 0.0

def fetch_24hr_volume(client, symbol):
    """Fetch the 24-hour trading volume for a given symbol."""
    try:
        ticker = client.get_ticker(symbol=symbol)
        return {
            'volume': float(ticker['volume']),
            'quoteVolume': float(ticker['quoteVolume'])
        }
    except Exception as e:
        log(f"Error fetching 24hr volume for {symbol}: {e}")
        return None


POSITIONS_FILE = "positions.json"

def save_entry_price(symbol, entry_price, quantity):
    """Save the entry price and quantity of a newly bought asset."""
    positions = {}

    # Load existing positions
    if os.path.exists(POSITIONS_FILE):
        with open(POSITIONS_FILE, "r") as f:
            positions = json.load(f)

    # Update or add the new position
    positions[symbol] = {
        "entry_price": entry_price,
        "quantity": quantity
    }

    # Save back to positions.json
    with open(POSITIONS_FILE, "w") as f:
        json.dump(positions, f, indent=4)

    log(f"Entry price for {symbol} saved: {entry_price} USDT | Quantity: {quantity}")


def place_market_order(client, symbol, side, quantity):
    """
    Place a market order and adjust quantity to meet Binance LOT_SIZE filter.
    """
    try:
        # Fetch symbol info to get the LOT_SIZE step size
        exchange_info = client.get_symbol_info(symbol)
        lot_size_filter = next(
            f for f in exchange_info['filters'] if f['filterType'] == 'LOT_SIZE'
        )
        step_size = float(lot_size_filter['stepSize'])
        precision = int(round(-math.log(step_size, 10), 0))

        # Adjust quantity to meet LOT_SIZE filter
        quantity = round(quantity, precision)

        # Place market order
        order = client.order_market(symbol=symbol, side=side, quantity=quantity)
        log(f"Market order placed: {order}")

        if side == "BUY":
            # Save entry price for new position
            entry_price = float(order['fills'][0]['price'])
            save_entry_price(symbol, entry_price, quantity)
            log(f"Saved entry price for {symbol}: {entry_price} USDT | Quantity: {quantity}")

        elif side == "SELL":
            # Remove sold position from positions.json
            if os.path.exists(POSITIONS_FILE):
                with open(POSITIONS_FILE, "r") as f:
                    positions = json.load(f)
                if symbol in positions:
                    del positions[symbol]
                    with open(POSITIONS_FILE, "w") as f:
                        json.dump(positions, f, indent=4)
                    log(f"Removed {symbol} from positions.json after SELL.")

        return order
    except Exception as e:
        log(f"Error placing market order for {symbol}: {e}")
        return None



