from src.fetch_prices import fetch_prices
from src.signal_engine import generate_signal

def run(symbol):
    success = fetch_prices(symbol)
    if not success:
        return {"error": "Failed to fetch stock data"}

    return generate_signal(symbol)
