import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense
from src.logger_config import setup_logger

logger = setup_logger("LSTM")

LOOKBACK = 60

os.makedirs("models", exist_ok=True)

def run_lstm(symbol):
    data_path = f"data/prices_{symbol}.csv"
    model_path = f"models/lstm_{symbol}.h5"

    df = pd.read_csv(data_path)
    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
    df = df.dropna()

    prices = df["Close"].values.reshape(-1, 1)

    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(prices)

    X, y = [], []
    for i in range(LOOKBACK, len(scaled)):
        X.append(scaled[i-LOOKBACK:i])
        y.append(scaled[i])

    X, y = np.array(X), np.array(y)

    if os.path.exists(model_path):
        logger.info(f"Loading existing model for {symbol}")
        model = load_model(model_path)
    else:
        logger.info(f"Training new model for {symbol}")
        model = Sequential([
            LSTM(50, input_shape=(X.shape[1], 1)),
            Dense(1)
        ])
        model.compile(optimizer="adam", loss="mse")
        model.fit(X, y, epochs=5, batch_size=32, verbose=0)
        model.save(model_path)
        logger.info(f"Model saved at {model_path}")

    last_window = scaled[-LOOKBACK:].reshape(1, LOOKBACK, 1)
    pred_scaled = model.predict(last_window, verbose=0)

    predicted_price = float(scaler.inverse_transform(pred_scaled)[0][0])
    latest_price = float(prices[-1][0])

    trend = "UP" if predicted_price > latest_price else "DOWN"

    return trend, predicted_price, latest_price
