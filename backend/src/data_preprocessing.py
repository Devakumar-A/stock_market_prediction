import pandas as pd
import os
import joblib
from sklearn.preprocessing import MinMaxScaler

# ===============================
# PATH SETUP
# ===============================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "stock_data.csv")
DATA_OUT_DIR = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.join(BASE_DIR, "models")

os.makedirs(DATA_OUT_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

# ===============================
# LOAD CLEAN YAHOO DATA
# ===============================
data = pd.read_csv(DATA_PATH)

# Expected columns: Date, Close
if not {"Date", "Close"}.issubset(data.columns):
    raise ValueError("CSV must contain Date and Close columns")

# ===============================
# DATE HANDLING
# ===============================
data["Date"] = pd.to_datetime(data["Date"])
data.sort_values("Date", inplace=True)
data.reset_index(drop=True, inplace=True)

# ===============================
# HANDLE MISSING VALUES
# ===============================
data.dropna(inplace=True)

# ===============================
# FEATURE SCALING
# ===============================
scaler = MinMaxScaler()
data["Close_Scaled"] = scaler.fit_transform(data[["Close"]])

# ===============================
# CREATE LAG FEATURES (FOR ML)
# ===============================
data["Lag_1"] = data["Close_Scaled"].shift(1)
data["Lag_2"] = data["Close_Scaled"].shift(2)
data["Lag_3"] = data["Close_Scaled"].shift(3)

data.dropna(inplace=True)

# ===============================
# STOCK NAME (ENV VARIABLE)
# ===============================
STOCK_NAME = os.environ.get("STOCK_NAME", "TCS")

# ===============================
# SAVE PROCESSED DATA
# ===============================
processed_path = os.path.join(DATA_OUT_DIR, f"TCS_processed.csv")
data.to_csv(processed_path, index=False)

# ===============================
# SAVE SCALER (PER STOCK)
# ===============================
scaler_path = os.path.join(MODEL_DIR, STOCK_NAME, "scaler.pkl")
os.makedirs(os.path.dirname(scaler_path), exist_ok=True)
joblib.dump(scaler, scaler_path)

print(f"✅ Preprocessing completed for {STOCK_NAME}")
print(f"📁 Data saved at: {processed_path}")
print(f"📁 Scaler saved at: {scaler_path}")
print(data.head())
