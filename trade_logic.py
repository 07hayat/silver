from functions import place_market_order, log, get_symbol_info, get_account_balance
from config import BINANCE_API_KEY, BINANCE_API_SECRET  # Import API keys
from binance.client import Client
import time
import math

def fetch_current_price(client, symbol):
    """Fetch the current live price of a symbol from Binance."""
    ticker = client.get_ticker(symbol=symbol)
    return float(ticker['lastPrice'])

def execute_daily_trading(client):
    """Identify top gainers and place trades for daily opportunities."""
    log("Starting daily trading...")

    try:
        tickers = client.get_ticker()
        usdt_balance = get_account_balance(client, "USDT")
        log(f"USDT Balance Retrieved: {usdt_balance}")
        if usdt_balance < 10:
            log("Insufficient USDT balance to trade.")
            return

        # Fetch top gainers
        top_gainers = sorted(
            tickers, key=lambda x: float(x['priceChangePercent']), reverse=True
        )[:5]  # Top 5 gainers

        for gainer in top_gainers:
            symbol = gainer['symbol']
            price_change = float(gainer['priceChangePercent'])
            latest_price = float(gainer['lastPrice'])
            volume = float(gainer['quoteVolume'])  # Example: Volume data

            log(f"Top Gainer: {symbol} | Latest Price: {latest_price} | Price Change: {price_change}% | Volume: {volume}")

            # Skip non-USDT pairs and pairs with low price change
            if "USDT" not in symbol:
                log(f"Skipping {symbol}. Not a USDT pair.")
                continue

            if price_change <= 1:
                log(f"Skipping {symbol}. Price change below threshold.")
                continue

            # Skip pairs with very low trading volume (example threshold: $1M)
            if volume < 1_000_000:
                log(f"Skipping {symbol}. Low trading volume: {volume}")
                continue

            # Place trade
            trade_amount = 35  # USDT to trade
            quantity = trade_amount / latest_price

            # Ensure quantity meets LOT_SIZE requirements
            exchange_info = client.get_symbol_info(symbol)
            lot_size_filter = next(
                f for f in exchange_info['filters'] if f['filterType'] == 'LOT_SIZE'
            )
            step_size = float(lot_size_filter['stepSize'])
            precision = int(round(-math.log(step_size, 10), 0))
            quantity = round(quantity, precision)

            try:
                log(f"Placing BUY order for {symbol} with {trade_amount} USDT...")
                order = place_market_order(client, symbol, "BUY", quantity)
                log(f"BUY order placed successfully for {symbol}. Order: {order}")
                break  # Trade one gainer per run
            except Exception as e:
                log(f"Error placing BUY order for {symbol}: {e}")

    except Exception as e:
        log(f"Error during daily trading: {e}")

def dynamic_profit_capture(client, symbol, entry_price, trailing_percent=2):
    """
    Monitor price for a trailing stop loss.
    """
    log(f"Starting trailing stop monitoring for {symbol}...")
    highest_price = entry_price
    trailing_stop_price = entry_price

    try:
        while True:
            ticker = client.get_ticker(symbol=symbol)
            current_price = float(ticker['lastPrice'])
            log(f"Current price of {symbol}: {current_price}")

            # Update highest price and trailing stop
            if current_price > highest_price:
                highest_price = current_price
                trailing_stop_price = highest_price * (1 - trailing_percent / 100)
                log(f"New highest price: {highest_price:.4f}. Adjusted trailing stop: {trailing_stop_price:.4f}")

            # Check if price hits trailing stop
            if current_price <= trailing_stop_price:
                log(f"Trailing stop hit for {symbol}. Selling at {current_price:.4f}...")
                quantity = get_account_balance(client, symbol.replace("USDT", ""))
                if quantity > 0:
                    place_market_order(client, symbol, "SELL", quantity)
                    log(f"Sold {quantity} of {symbol} at {current_price:.4f}. Removing from positions.json...")
                break  # Exit monitoring loop

            time.sleep(5)  # Avoid API flooding

    except Exception as e:
        log(f"Error in trailing stop monitoring for {symbol}: {e}")


def main():
    print("Executing trade logic...")
    
    # Initialize Binance client
    client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
    
    # Fetch account balance for USDT
    usdt_balance = get_account_balance(client, "USDT")
    print(f"USDT Balance: {usdt_balance}")
    
    # Fetch current price of BTC/USDT
    symbol = "BTCUSDT"
    price = fetch_current_price(client, symbol)
    print(f"Current price of {symbol}: {price}")
    
    # Example: Place a market order (simulation, commented out for safety)
    # order = place_market_order(client, symbol, "BUY", 0.001)
    # print(f"Order placed: {order}")

    print("Trade logic executed successfully.")

if __name__ == "__main__":
    main()
