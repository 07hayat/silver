
from functions import log

def track_holdings(holdings):
    for symbol, amount in holdings.items():
        log(f"Holding: {symbol} - {amount}")
