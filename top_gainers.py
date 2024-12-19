from functions import log

def detect_top_gainers(client):
    """
    Detect top gainers in the last 24 hours.
    Returns the first symbol with a price change exceeding the threshold.
    """
    TOP_GAINER_THRESHOLD = 10  # Percentage gain to qualify
    try:
        tickers = client.get_ticker()
        for ticker in tickers:
            symbol = ticker['symbol']
            if not symbol.endswith("USDT"):  # Focus only on USDT pairs
                continue

            price_change_percent = float(ticker['priceChangePercent'])
            if price_change_percent >= TOP_GAINER_THRESHOLD:
                log(f"Top Gainer Detected: {symbol} - Price Change: {price_change_percent}%")
                return symbol
    except Exception as e:
        log(f"Error detecting top gainers: {e}")
    return None
