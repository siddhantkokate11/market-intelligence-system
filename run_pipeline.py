from src.fetch_prices import fetch_prices
from src.signal_engine import generate_signal

def run(symbol):
    fetch_prices(symbol)
    return generate_signal(symbol)

if __name__ == "__main__":
    print(run("TCS.NS"))
