import streamlit as st
import pandas as pd
import time
import os
import json
import logging
from binance.client import Client
from config import BINANCE_API_KEY, BINANCE_API_SECRET, DEBUG_MODE
import random
# Binance Client Initialization
client = Client(BINANCE_API_KEY, BINANCE_API_SECRET) if DEBUG_MODE == "real" else None

# Page Configuration
st.set_page_config(page_title="Binance Trading Bot Dashboard", layout="wide")

# Real Data Functions

def get_summary_stats():
    try:
        # Fetch account balance and latest prices
        account_info = client.get_account()
        tickers = client.get_symbol_ticker()

        # Map symbol prices
        price_dict = {ticker['symbol']: float(ticker['price']) for ticker in tickers}

        # Initialize balances and PnL
        total_usdt_balance = 0.0
        total_balance_in_usdt = 0.0
        unrealized_pnl = 0.0

        # Load positions (entry prices)
        positions = {}
        if os.path.exists("positions.json"):
            with open("positions.json", "r") as f:
                positions = json.load(f)

        # Iterate over account balances
        for asset in account_info['balances']:
            free = float(asset['free'])
            locked = float(asset['locked'])
            total_amount = free + locked

            if total_amount > 0:
                if asset['asset'] == "USDT":
                    total_usdt_balance += total_amount
                else:
                    # Calculate balance converted to USDT using price
                    symbol = f"{asset['asset']}USDT"
                    if symbol in price_dict:
                        current_price = price_dict[symbol]
                        total_balance_in_usdt += total_amount * current_price

                        # Calculate Unrealized PnL if entry price exists
                        if symbol in positions:
                            entry_price = positions[symbol]["entry_price"]
                            pnl = (current_price - entry_price) * total_amount
                            unrealized_pnl += pnl

        # Total Balance = USDT balance + other holdings in USDT
        total_balance_in_usdt += total_usdt_balance

        return {
            "Profit Today": 0.0,  # Placeholder
            "Profit 7 Days": 0.0,  # Placeholder
            "Unrealized PnL": round(unrealized_pnl, 2),
            "USDT Balance": round(total_usdt_balance, 2),
            "Trades Today": 0,  # Placeholder
            "Balance": round(total_balance_in_usdt, 2),
        }

    except Exception as e:
        st.error(f"Error fetching summary stats: {e}")
        return {
            "Profit Today": 0.0,
            "Profit 7 Days": 0.0,
            "Unrealized PnL": 0.0,
            "USDT Balance": 0.0,
            "Trades Today": 0,
            "Balance": 0.0,
        }

def get_new_listings():
    try:
        if DEBUG_MODE == "debug":
            # Return mock data in debug mode
            return pd.DataFrame([
                {"Symbol": "NEWUSDT1", "Category": "Meme", "Change %": "+5.23%", "Volume Spike %": "150%"},
                {"Symbol": "NEWUSDT2", "Category": "NFT", "Change %": "+7.10%", "Volume Spike %": "200%"}
            ])
        else:
            # Fetch tickers and filter only USDT pairs
            tickers = client.get_ticker()
            usdt_pairs = [ticker for ticker in tickers if ticker['symbol'].endswith('USDT')]

            # Sort by highest percentage change
            sorted_pairs = sorted(usdt_pairs, key=lambda x: float(x['priceChangePercent']), reverse=True)

            # Create a DataFrame with the top new listings
            return pd.DataFrame([
                {
                    "Symbol": t['symbol'],
                    "Category": "Standard",  # Default placeholder category
                    "Change %": f"{t['priceChangePercent']}%",
                    "Volume Spike %": f"{float(t['quoteVolume']):.2f}"
                }
                for t in sorted_pairs[:10]  # Top 10 new USDT pairs
            ])

    except Exception as e:
        st.error(f"Error fetching new listings: {e}")
        return pd.DataFrame()

def get_top_gainers():
    if DEBUG_MODE == "debug":
        # Return mock data in debug mode
        return pd.DataFrame([{"Symbol": "BTCUSDT", "Latest Price ($)": 50000, "Price % Change": "+10%", "Volume ($)": 200000}])
    else:
        try:
            # Fetch tickers and filter USDT pairs
            tickers = client.get_ticker()
            usdt_pairs = [t for t in tickers if "USDT" in t['symbol'] and t['symbol'] != "USDTUSDT"]

            # Sort by percentage change and take the top 10
            top_gainers = sorted(usdt_pairs, key=lambda x: float(x['priceChangePercent']), reverse=True)[:10]

            # Create DataFrame for display
            return pd.DataFrame([
                {"Symbol": t['symbol'], 
                 "Latest Price ($)": round(float(t['lastPrice']), 6),
                 "Price % Change": f"{float(t['priceChangePercent']):.3f}%",
                 "Volume ($)": round(float(t['quoteVolume']), 2)}
                for t in top_gainers
            ])
        except Exception as e:
            st.error(f"Error fetching top gainers: {e}")
            return pd.DataFrame()


# Global cache to store previous trailing prices
previous_trailing_prices = {}  # Initialize at the top level

def get_running_positions():
    try:
        global previous_trailing_prices  # Declare the global cache

        if DEBUG_MODE == "debug":
            # Return mock positions in debug mode
            return pd.DataFrame([
                {"Symbol": "BTC", "Total Lot": "0.005", "Size (%)": "20.00%",
                 "Entry Price ($)": "50000.00", "PnL %": "+5.00%", "Trailing": "50050.00"},
                {"Symbol": "ETH", "Total Lot": "0.1", "Size (%)": "30.00%",
                 "Entry Price ($)": "3000.00", "PnL %": "-2.50%", "Trailing": "2990.00"}
            ])

        # Real data fetching
        account_info = client.get_account()
        tickers = client.get_symbol_ticker()

        # Create price lookup dictionary
        price_dict = {ticker['symbol']: float(ticker['price']) for ticker in tickers}

        positions = []
        total_balance_usdt = 0.0

        # Step 1: Calculate total USDT equivalent balance
        for asset in account_info['balances']:
            free = float(asset['free'])
            locked = float(asset['locked'])
            total_amount = free + locked

            if total_amount > 0:
                symbol = f"{asset['asset']}USDT"
                if asset['asset'] == "USDT":
                    total_balance_usdt += total_amount
                elif symbol in price_dict:
                    total_balance_usdt += total_amount * price_dict[symbol]

        # Step 2: Populate positions list with trailing price logic
        for asset in account_info['balances']:
            free = float(asset['free'])
            locked = float(asset['locked'])
            total_amount = free + locked

            if total_amount > 0:
                symbol = f"{asset['asset']}USDT"
                if asset['asset'] == "USDT":
                    current_price = 1.0  # USDT price is always 1.0
                elif symbol in price_dict:
                    current_price = price_dict[symbol]
                else:
                    continue  # Skip assets without USDT pairs

                # Calculate size percentage
                size_percentage = (total_amount * current_price / total_balance_usdt) * 100

                # Fetch trailing price from previous_trailing_prices or initialize
                trailing_price = previous_trailing_prices.get(symbol, current_price)

                # Adjust trailing price logic (e.g., for a trailing stop strategy)
                if current_price > trailing_price:
                    trailing_price = current_price  # Adjust trailing price upwards

                # Update the global cache
                previous_trailing_prices[symbol] = trailing_price

                # Append position
                positions.append({
                    "Symbol": asset['asset'],
                    "Total Lot": f"{total_amount:.6f}",
                    "Size (%)": f"{size_percentage:.2f}%",
                    "Entry Price ($)": f"{current_price:.2f}",
                    "PnL %": "0.00%",  # Placeholder PnL
                    "Trailing": f"{trailing_price:.2f}"
                })

        return pd.DataFrame(positions)

    except Exception as e:
        st.error(f"Error fetching running positions: {e}")
        return pd.DataFrame()


def process_log_messages(logs):
    # Map raw messages to user-friendly text
    message_map = {
        "connected": "Connected to Binance",
        "order success": "Order executed successfully",
        "sell success": "Sell order completed",
    }

    # Replace mapped messages
    logs['Message'] = logs['Message'].replace(message_map)

    # Shorten overly long log messages
    def shorten_message(message):
        if "Account Summary" in message:
            return message  # Leave summarized messages untouched
        elif "Connected: Successfully connected to Binance API. Account:" in message:
            return "Connected: Binance API account details fetched."
        elif len(message) > 200:  # Shorten overly long messages
            return message[:200] + "..."
        return message  # Default: Keep other messages as-is

    logs['Message'] = logs['Message'].apply(shorten_message)
    return logs

def get_logs(recent_lines=20):
    """
    Reads logs from bot_activity.log and returns the last `recent_lines` in reverse order for display (last message at the top).
    """
    log_file = "logs/bot_activity.log"
    print(f"[DEBUG] Reading from: {log_file}")

    if not os.path.exists(log_file):
        print("[DEBUG] Log file not found.")
        return pd.DataFrame([{"Timestamp": "-", "Level": "INFO", "Message": "No recent logs available"}])

    with open(log_file, "r") as file:
        lines = file.readlines()
        print(f"[DEBUG] Found {len(lines)} lines in log file.")

    # Keep only the last `recent_lines` and reverse them
    lines = lines[-recent_lines:][::-1]

    logs = []
    for line in lines:
        parts = line.strip().split("|", maxsplit=2)
        if len(parts) == 3:
            logs.append({"Timestamp": parts[0].strip(), "Level": parts[1].strip(), "Message": parts[2].strip()})

    if logs:
        df_logs = pd.DataFrame(logs)
        return process_log_messages(df_logs)  # Apply processing
    else:
        print("[DEBUG] No logs parsed.")
        return pd.DataFrame([{"Timestamp": "-", "Level": "INFO", "Message": "No recent logs available"}])

# CSS for Styling
st.markdown(
    """
    <style>
    .metric-box {
        border-radius: 8px;
        padding: 15px;
        color: white;
        text-align: center;
        font-size: 1.2em;
        margin: 5px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
    }
    .zebra-table tr:nth-child(even) {background-color: #f2f2f2;}
    .zebra-table th, .zebra-table td {
        padding: 8px;
        text-align: center;
    }
    .zebra-table th {
        background-color: #1E90FF;
        color: white;
        font-weight: bold;
    }
    .royalblue { background-color: #4169E1; }
    .dodgerblue { background-color: #1E90FF; }
    .tomato { background-color: #FF6347; }
    .coral { background-color: #FF7F50; }
    .darkgray { background-color: #A9A9A9; }
    .red { background-color: #FF0000; }
    </style>
    """,
    unsafe_allow_html=True
)

# ================= Layout =================
placeholder = st.empty()

while True:
    with placeholder.container():
        # Full Header
        st.markdown("<h1 style='text-align: center;'>📊 Binance Trading Bot Dashboard</h1>", unsafe_allow_html=True)

        # Summary Metrics - Color Coded Boxes
        summary = get_summary_stats()
        st.markdown("<br>", unsafe_allow_html=True)  # Adding space under the title
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        col1.markdown(f"<div class='metric-box royalblue'>Profit Today<br><b>${summary['Profit Today']}</b></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='metric-box dodgerblue'>Profit 7 Days<br><b>${summary['Profit 7 Days']}</b></div>", unsafe_allow_html=True)
        col3.markdown(f"<div class='metric-box tomato'>Unrealized PnL<br><b>${summary['Unrealized PnL']}</b></div>", unsafe_allow_html=True)
        col4.markdown(f"<div class='metric-box coral'>USDT Balance<br><b>${summary['USDT Balance']}</b></div>", unsafe_allow_html=True)
        col5.markdown(f"<div class='metric-box darkgray'>Trades Today<br><b>{summary['Trades Today']}</b></div>", unsafe_allow_html=True)
        col6.markdown(f"<div class='metric-box red'>Balance<br><b>${summary['Balance']}</b></div>", unsafe_allow_html=True)

        st.markdown("---")

        # Four Column Section
        col1, col2, col3, col4 = st.columns(4)

        # Top Gainers
        with col1:
            st.markdown("### 🏆 Top Gainers %")
            top_gainers = get_top_gainers()
            st.markdown(top_gainers.to_html(classes="zebra-table", index=False), unsafe_allow_html=True)

        # New Listings
        with col2:
            st.markdown("### ✨ New Listings")
            new_listings = get_new_listings()
            st.markdown(new_listings.to_html(classes="zebra-table", index=False), unsafe_allow_html=True)

        # Running Positions
        with col3:
            st.markdown("### 📊 Running Positions")
            running_positions = pd.DataFrame(get_running_positions())
            st.markdown(running_positions.to_html(classes="zebra-table", index=False), unsafe_allow_html=True)

        # Recent Logs
        with col4:
            st.markdown("### 📜 Recent Logs")
            logs = get_logs()
            if not logs.empty:
                # Convert logs to HTML with zebra-table styling
                st.markdown(
                    logs.to_html(classes="zebra-table", index=False, escape=False),
                    unsafe_allow_html=True
                )
            else:
                st.markdown("No recent logs available.")

    # Auto Refresh Every 10 Seconds
    time.sleep(10)

