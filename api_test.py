from binance.client import Client
from config import BINANCE_API_KEY, BINANCE_API_SECRET

try:
    # Initialize Binance client
    client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)

    # Test connectivity: Get server time
    server_time = client.get_server_time()
    print("Server Time:", server_time)

    # Test tickers
    tickers = client.get_ticker()
    print("Ticker sample:", tickers[:5])  # Print first 5 tickers
except Exception as e:
    print(f"Error connecting to Binance API: {e}")
