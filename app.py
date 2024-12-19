import streamlit as st

# Title for the dashboard
st.title("Trading Bot Dashboard")

# Example: Display USDT Balance
usdt_balance = 486.34  # Replace with dynamic value from your bot
st.metric(label="USDT Balance", value=f"${usdt_balance:.2f}")

# Example: Display Top Gainers
st.subheader("Top Gainers")
top_gainers = [
    {"Symbol": "PENGUUSDT", "Latest Price ($)": 0.037528, "Price % Change": 33.149, "Volume ($)": 4.865760e8},
    {"Symbol": "USUALUSDT", "Latest Price ($)": 1.057300, "Price % Change": 25.734, "Volume ($)": 7.724420e8},
]
st.table(top_gainers)
