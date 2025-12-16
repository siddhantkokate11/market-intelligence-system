import yfinance as yf
import pandas as pd
from src.logger_config import setup_logger

logger = setup_logger("FetchPrices")

def fetch_prices(symbol):
    logger.info(f"Fetching stock price data for {symbol}")

    try:
        df = yf.download(
            symbol,
            period="2y",        # more reliable than dates
            interval="1d",
            progress=False,
            threads=False
        )
    except Exception as e:
        logger.error(f"yfinance error: {e}")
        return False

    if df is None or df.empty:
        logger.error(f"No data fetched for {symbol}")
        return False

    df.reset_index(inplace=True)
    df.to_csv(f"data/prices_{symbol}.csv", index=False)

    logger.info(f"Saved data/prices_{symbol}.csv")
    return True
