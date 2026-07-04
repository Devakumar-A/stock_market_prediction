from flask import Flask, request, jsonify, render_template
import joblib
import numpy as np
import os
import pandas as pd
from tensorflow.keras.models import load_model

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

# ===============================
# BASE DIRECTORY
# ===============================
BASE_DIR = os.path.dirname(__file__)

# ===============================
# HELPER: REAL 60-DAY WINDOW
# ===============================
def get_last_60_closes(stock):
    path = os.path.join(BASE_DIR, "data", f"{stock}_processed.csv")
    df = pd.read_csv(path)

    if "Close" not in df.columns:
        raise ValueError("Processed file must contain Close column")

    closes = df["Close"].values
    if len(closes) < 60:
        raise ValueError("Not enough data for LSTM (need at least 60 rows)")

    return closes[-60:]

# ===============================
# LINEAR REGRESSION (MULTI-STOCK)
# ===============================
def load_model_and_scaler(stock):
    model_path = os.path.join(BASE_DIR, "models", stock, "linear_regression.pkl")
    scaler_path = os.path.join(BASE_DIR, "models", stock, "scaler.pkl")

    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)

    return model, scaler

# ===============================
# LOAD LSTM MODEL (REAL)
# ===============================
LSTM_MODEL_PATH = os.path.join(BASE_DIR, "models", "LSTM", "lstm_model.keras")
LSTM_SCALER_PATH = os.path.join(BASE_DIR, "models", "LSTM", "scaler.pkl")

lstm_model = load_model(LSTM_MODEL_PATH, compile=False)
lstm_scaler = joblib.load(LSTM_SCALER_PATH)

# ===============================
# ROUTES
# ===============================
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json

        # -------------------------------
        # INPUTS (SCALED)
        # -------------------------------
        lag_1 = float(data["lag_1"])
        lag_2 = float(data["lag_2"])
        lag_3 = float(data["lag_3"])

        stock = data.get("stock", "AAPL")
        model_type = data.get("model_type", "ml")  # ml | dl

        # ===============================
        # ML: LINEAR REGRESSION
        # ===============================
        if model_type == "ml":
            model, scaler = load_model_and_scaler(stock)

            # for chart (new feature)
            last_60 = get_last_60_closes(stock)

            lags = np.array([[lag_1, lag_2, lag_3]])
            scaled_pred = model.predict(lags)[0]
            predicted_price = scaler.inverse_transform([[scaled_pred]])[0][0]

            price_yesterday = scaler.inverse_transform([[lag_1]])[0][0]
            price_2_days = scaler.inverse_transform([[lag_2]])[0][0]
            price_3_days = scaler.inverse_transform([[lag_3]])[0][0]

        # ===============================
        # DL: REAL LSTM
        # ===============================
        else:
            last_60 = get_last_60_closes(stock)

            scaled_seq = lstm_scaler.transform(last_60.reshape(-1, 1))
            X = scaled_seq.reshape(1, 60, 1)

            scaled_pred = lstm_model.predict(X, verbose=0)[0][0]
            predicted_price = lstm_scaler.inverse_transform([[scaled_pred]])[0][0]

            price_3_days, price_2_days, price_yesterday = last_60[-3:]

        # ===============================
        # TREND & CONFIDENCE
        # ===============================
        trend = "UP 📈" if predicted_price > price_yesterday else "DOWN 📉"

        volatility = abs(price_yesterday - price_3_days)
        confidence = max(70, min(95, int(100 - volatility * 10)))

        explanation = (
            "Linear Regression predicts using recent lag features, "
            "while LSTM predicts using a rolling 60-day historical window."
        )
        # Dates for chart
        dates_60 = pd.read_csv(
            os.path.join(BASE_DIR, "data", f"{stock}_processed.csv")
        )["Date"].tail(60).tolist()

        predicted_date = (pd.to_datetime(dates_60[-1]) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
        if trend.startswith("UP"):
            market_summary = "The model predicts an upward trend with moderate confidence based on recent momentum."
        else:
            market_summary = "The model predicts a downward trend indicating recent weakness in price movement."

        # ===============================
        # RESPONSE (BACKWARD COMPATIBLE)
        # ===============================
        return jsonify({
            "predicted_price": round(predicted_price, 2),
            "trend": trend,
            "confidence": confidence,
            "explanation": explanation,
            "dates_60": dates_60 + [predicted_date],
            "market_summary": market_summary,

            # OLD FEATURE (kept)
            "previous_prices": [
                round(price_3_days, 2),
                round(price_2_days, 2),
                round(price_yesterday, 2)
            ],

            # NEW FEATURE (60-day history)
            "history_60": [round(p, 2) for p in last_60]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===============================
# RUN SERVER
# ===============================
if __name__ == "__main__":
    app.run(debug=True)
