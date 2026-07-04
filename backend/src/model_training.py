import pandas as pd
import os
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# ===============================
# PATH SETUP
# ===============================
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed_data.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "linear_regression.pkl")

os.makedirs(MODEL_DIR, exist_ok=True)

# ===============================
# LOAD DATA
# ===============================
data = pd.read_csv(DATA_PATH)

X = data[['Lag_1', 'Lag_2', 'Lag_3']]
y = data['Close_Scaled']

# ===============================
# TRAIN–TEST SPLIT (TIME SERIES SAFE)
# ===============================
split_index = int(len(data) * 0.8)

X_train, X_test = X[:split_index], X[split_index:]
y_train, y_test = y[:split_index], y[split_index:]

# ===============================
# TRAIN MODEL
# ===============================
model = LinearRegression()
model.fit(X_train, y_train)

# ===============================
# PREDICT & EVALUATE
# ===============================
y_pred = model.predict(X_test)

mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

# ===============================
# SAVE MODEL
# ===============================
joblib.dump(model, MODEL_PATH)

print("✅ Model trained successfully!")
print(f"📁 Model saved at: {MODEL_PATH}")
print(f"📊 Mean Squared Error (MSE): {mse:.6f}")
print(f"📈 R² Score: {r2:.4f}")
