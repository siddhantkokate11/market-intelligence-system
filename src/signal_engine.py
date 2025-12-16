from datetime import datetime
import pandas as pd
from src.lstm_model import run_lstm
from src.logger_config import setup_logger

logger = setup_logger("SignalEngine")

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def generate_signal(symbol):
    # ---- Load price data ----
    price_df = pd.read_csv(f"data/prices_{symbol}.csv")

    price_df["Close"] = pd.to_numeric(price_df["Close"], errors="coerce")
    price_df = price_df.dropna()

    # ---- Indicators ----
    price_df["SMA_20"] = price_df["Close"].rolling(20).mean()
    price_df["RSI"] = calculate_rsi(price_df["Close"])

    latest_rsi = float(price_df["RSI"].iloc[-1])
    latest_sma = float(price_df["SMA_20"].iloc[-1])
    latest_price = float(price_df["Close"].iloc[-1])

    # ---- LSTM ----
    trend, predicted_price, _ = run_lstm(symbol)

    # ---- Signal Logic ----
    if trend == "UP" and latest_rsi < 70 and latest_price > latest_sma:
        signal = "BUY"
    elif trend == "DOWN" and latest_rsi > 30:
        signal = "SELL"
    else:
        signal = "HOLD"

    result = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "symbol": symbol,
        "trend": trend,
        "signal": signal,
        "latest_price": round(latest_price, 2),
        "predicted_price": round(predicted_price, 2),
        "RSI": round(latest_rsi, 2),
        "SMA_20": round(latest_sma, 2)
    }

    # ---- Save history ----
    pd.DataFrame([result]).to_csv(
        "data/signals.csv",
        mode="a",
        header=not pd.io.common.file_exists("data/signals.csv"),
        index=False
    )

    logger.info(f"Signal generated for {symbol}: {signal}")
    return result
