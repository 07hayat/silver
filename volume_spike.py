from functions import log, fetch_24hr_volume

def detect_volume_spike(client, symbols):
    """
    Detect symbols with significant volume spikes.
    Returns the first symbol with a volume increase exceeding the threshold.
    """
    VOLUME_SPIKE_THRESHOLD = 2.5  # Volume must be 2.5x the average to trigger
    try:
        for symbol in symbols:
            volume_data = fetch_24hr_volume(client, symbol)
            if not volume_data:
                continue

            volume = volume_data['volume']
            avg_volume = volume_data['quoteVolume'] / 24
            if volume > avg_volume * VOLUME_SPIKE_THRESHOLD:
                log(f"Volume Spike Detected: {symbol} - Volume: {volume}, Avg: {avg_volume}")
                return symbol
    except Exception as e:
        log(f"Error detecting volume spikes: {e}")
    return None
