import pandas as pd
import os
import joblib
import matplotlib.pyplot as plt

# ===============================
# PATH SETUP
# ===============================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed_data.csv")
MODEL_PATH = os.path.join(BASE_DIR, "models", "linear_regression.pkl")
OUTPUT_DIR = os.path.join(BASE_DIR, "..", "outputs")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ===============================
# LOAD DATA & MODEL
# ===============================
data = pd.read_csv(DATA_PATH)
model = joblib.load(MODEL_PATH)

X = data[['Lag_1', 'Lag_2', 'Lag_3']]
y_actual = data['Close_Scaled']
y_pred = model.predict(X)

# ===============================
# PLOT
# ===============================
plt.figure()
plt.plot(y_actual, label="Actual")
plt.plot(y_pred, label="Predicted")
plt.legend()
plt.title("Stock Price Prediction (Scaled)")
plt.savefig(os.path.join(OUTPUT_DIR, "prediction_plot.png"))
plt.show()

print("✅ Prediction graph generated and saved!")
