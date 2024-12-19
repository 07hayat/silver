
from functions import log

def detect_hot_gainers(ticker_data, threshold):
    for symbol, data in ticker_data.items():
        price_change = float(data["priceChangePercent"])
        if price_change > threshold:
            log(f"Gainer Detected: {symbol} - {price_change}%")
            return symbol
    return None
