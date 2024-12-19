
# Centralized Configuration Settings

DEBUG_MODE = "real"  # Change to "debug" for testing
BINANCE_API_KEY = "hAQi2J7LPMHHUrumiUvGpvAaB1U3uLbovxrqQIp9fTAIqBWkUqJqSMidpuKBt2YF"
BINANCE_API_SECRET = "OiTmse2rfm7NiCsiUpTYSbwH5MhASgVVY5KZZUIYviitwYiqjowmWsK3wKzTx9Rc"

# Debug Data Simulation Settings
SIMULATED_BALANCE = 2500.00
SIMULATED_TRADES_TODAY = 100
SIMULATED_PROFIT_TODAY = 150.00

# Bot Settings
FETCH_PAIRS_LOG = True  # Enable or disable logging for fetching trading pairs
NEW_LISTING_INTERVAL = 5  # Interval in minutes for checking new listings
VOLUME_SPIKE_THRESHOLD = 1.5  # Volume spike multiplier threshold
PROFIT_MARGIN_PERCENT = 10  # Target profit margin for buy/sell strategy
ENABLE_VOLUME_SPIKE_STRATEGY = True  # Toggle volume spike trading
ENABLE_NEW_LISTINGS_STRATEGY = True  # Toggle new listings strategy
ENABLE_PROFIT_TAKING = True  # Toggle profit-taking strategy

# API Retry Settings
API_RETRY_LIMIT = 5
API_RETRY_DELAY = 2  # Delay in seconds between retries
