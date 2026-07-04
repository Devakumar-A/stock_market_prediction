import pandas as pd
import numpy as np
import os
import joblib
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping

# ===============================
# PATHS
# ===============================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "stock_data.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models", "LSTM")

os.makedirs(MODEL_DIR, exist_ok=True)

# ===============================
# LOAD DATA
# ===============================
df = pd.read_csv(DATA_PATH)

# Handle Yahoo CSV format
if "Date" not in df.columns:
    df = pd.read_csv(DATA_PATH, skiprows=2)
    df.columns = ["Date", "Close", "High", "Low", "Open", "Volume"]

df = df[["Date", "Close"]]
df["Date"] = pd.to_datetime(df["Date"])
df.set_index("Date", inplace=True)
df.dropna(inplace=True)

# ===============================
# SCALE DATA
# ===============================
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(df[["Close"]])

# Save scaler
joblib.dump(scaler, os.path.join(MODEL_DIR, "scaler.pkl"))

# ===============================
# CREATE SEQUENCES
# ===============================
def create_sequences(data, window=60):
    X, y = [], []
    for i in range(window, len(data)):
        X.append(data[i-window:i, 0])
        y.append(data[i, 0])
    return np.array(X), np.array(y)

WINDOW_SIZE = 60
X, y = create_sequences(scaled_data, WINDOW_SIZE)

# Train-test split (time-series safe)
split = int(0.8 * len(X))
X_train, X_test = X[:split], X[split:]
y_train, y_test = y[:split], y[split:]

# Reshape for LSTM
X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
X_test = X_test.reshape((X_test.shape[0], X_test.shape[1], 1))

# ===============================
# BUILD LSTM MODEL
# ===============================
model = Sequential([
    LSTM(50, return_sequences=False, input_shape=(WINDOW_SIZE, 1)),
    Dense(1)
])

model.compile(optimizer="adam", loss="mse")

# ===============================
# TRAIN MODEL
# ===============================
early_stop = EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True)

model.fit(
    X_train, y_train,
    epochs=30,
    batch_size=32,
    validation_data=(X_test, y_test),
    callbacks=[early_stop],
    verbose=1
)

# ===============================
# SAVE MODEL
# ===============================
model.save(os.path.join(MODEL_DIR, "lstm_model.keras"))


print("✅ LSTM model trained and saved successfully!")
