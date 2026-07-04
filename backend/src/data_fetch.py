import yfinance as yf
import pandas as pd
import os

# ===============================
# CONFIG
# ===============================
STOCK_SYMBOL = "AAPL"   # Change to INFY.NS / TCS.NS when needed
PERIOD = "5y"

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

OUTPUT_PATH = os.path.join(DATA_DIR, "stock_data.csv")

# ===============================
# FETCH DATA
# ===============================
df = yf.download(STOCK_SYMBOL, period=PERIOD, progress=False)

if df.empty:
    raise ValueError("❌ No data downloaded. Check stock symbol.")

# Reset index to get Date column
df.reset_index(inplace=True)

# Keep only required columns
required_cols = ["Date", "Close"]
df = df[required_cols]

# Save
df.to_csv(OUTPUT_PATH, index=False)

print(f"✅ Data fetched for {STOCK_SYMBOL}")
print(f"✅ Saved to {OUTPUT_PATH}")
