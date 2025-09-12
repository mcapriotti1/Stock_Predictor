from yahooquery import Ticker
from datetime import date
from database import database
from models import actuals, predictions, maes, days, daily_maes
from backend.myModel import run_prediction
import sqlite3
import joblib
from sqlalchemy import select, delete, asc

MAX_ACTUALS = 31
MAX_PREDICTIONS = 11

# ----------------- Helper functions ----------------- #

async def get_tickers():
    query = select(maes.c.ticker)
    rows = await database.fetch_all(query)
    return [row["ticker"] for row in rows]

async def get_latest_prices(tickers):
    ticker_obj = Ticker(tickers)
    prices = ticker_obj.history(period="1d") 
    prices = prices.reset_index()
    return prices

async def insert_actual(ticker, row):
    actual_date = row["date"].date() if hasattr(row["date"], "date") else row["date"]
    try:
        query = actuals.insert().values(
            ticker=ticker,
            date=actual_date,
            open=row["open"],
            close=row["close"],
            high=row["high"],
            low=row["low"],
            volume=row["volume"],
        )
        await database.execute(query)
        print(f"Inserted actual for {ticker} on {actual_date}")
    except sqlite3.IntegrityError:
        print(f"ctual for {ticker} on {actual_date} already exists")

async def trim_actuals(ticker):
    query = select(actuals).where(actuals.c.ticker == ticker).order_by(asc(actuals.c.date))
    rows = await database.fetch_all(query)
    if len(rows) > MAX_ACTUALS:
        dates_to_delete = [r["date"] for r in rows[:-MAX_ACTUALS]]
        del_query = delete(actuals).where((actuals.c.ticker == ticker) & (actuals.c.date.in_(dates_to_delete)))
        await database.execute(del_query)
        print(f"Deleted {len(dates_to_delete)} oldest actuals for {ticker}")

async def trim_predictions(ticker):
    query = select(predictions).where(predictions.c.ticker == ticker).order_by(asc(predictions.c.date))
    rows = await database.fetch_all(query)
    if len(rows) > MAX_PREDICTIONS:
      dates_to_delete = [r["date"] for r in rows[:-MAX_PREDICTIONS]]
      del_query = delete(predictions).where((predictions.c.ticker == ticker) & (predictions.c.date.in_(dates_to_delete)))
      await database.execute(del_query)
      print(f"Deleted {len(dates_to_delete)} oldest predictions for {ticker}")

async def get_next_trading_day(today):
    if not today:
        print("No trading days found in DB!")
        return []
    
    next_day_query = (
        select(days.c.date)
        .where(days.c.date > today)
        .order_by(asc(days.c.date))
        .limit(1)
    )

    trading_day = await database.fetch_one(next_day_query)    

    next_trading_day = trading_day["date"]

    actual_exists_query = (
        select(actuals.c.date)
        .where(actuals.c.date == next_trading_day)
        .limit(1)
    )
    existing = await database.fetch_one(actual_exists_query)

    if existing:
        print(f"Skipping {trading_day}, already exists in actuals")
        return []
    return next_trading_day

async def insert_prediction(ticker, prediction_date, all_models):
    query = predictions.select().where(
        (predictions.c.ticker == ticker) &
        (predictions.c.date == prediction_date)
    )
    existing = await database.fetch_one(query)

    if existing:
        print(f"Prediction for {ticker} on {prediction_date} already exists")
        return existing["prediction"], None 

    pred_value, MAE = await run_prediction(ticker, all_models, prediction_date)

    query = predictions.insert().values(
        ticker=ticker,
        date=prediction_date,
        prediction=pred_value,
    )
    await database.execute(query)
    print(f"Inserted prediction for {ticker} on {prediction_date}: {pred_value}")

    return pred_value, MAE

async def calculate_and_store_daily_mae(ticker, today):
    actuals_query = (
        select(actuals.c.date, actuals.c.close.label("actual_close"))
        .where(actuals.c.ticker == ticker)
        .order_by(asc(actuals.c.date))
    )
    actual_rows = await database.fetch_all(actuals_query)
    last_10_actuals = actual_rows[-10:]
    print([row["actual_close"] for row in last_10_actuals])

    if len(last_10_actuals) < 1:
        print(f"Not enough actuals to calculate MAE for {ticker}")
        return

    predictions_query = (
        select(predictions.c.date, predictions.c.prediction.label("pred_close"))
        .where((predictions.c.ticker == ticker) & (predictions.c.date <= today))
        .order_by(asc(predictions.c.date))
    )
    pred_rows = await database.fetch_all(predictions_query)
    last_10_preds = pred_rows[-10:]
    print([row["pred_close"] for row in last_10_preds])

    if len(last_10_preds) < 1:
        print(f"Not enough predictions to calculate MAE for {ticker}")
        return

    paired = zip(last_10_actuals, last_10_preds)

    errors = [100 * (abs(a["actual_close"] - p["pred_close"]) / a["actual_close"]) for a, p in paired]
    print(errors)
    mae_value = sum(errors) / len(errors)

    try:
        insert_query = daily_maes.insert().values(
            ticker=ticker,
            date=today,
            mae=mae_value,
        )
        await database.execute(insert_query)
        print(f"📊 Stored daily MAE for {ticker} on {today}: {mae_value:.4f}")
    except sqlite3.IntegrityError:
        print(f"⚠️ MAE for {ticker} on {today} already exists")

def get_today():
    ticker_obj = Ticker("AAPL")
    prices = ticker_obj.history(period="1d").reset_index()
    last_date = prices['date'].iloc[-1]

    today = last_date
    return today

# ----------------- Main daily job ----------------- #

async def run_daily_job():
    print("Starting daily job...")
    await database.connect()
    all_models = joblib.load("all_models.joblib")

    tickers = await get_tickers()
    print(f"Tickers to process: {tickers}")

    today = get_today()
    tomorrow = await get_next_trading_day(today)
    print(f"Next trading day for predictions: {tomorrow}")

    prices = None
    if tomorrow:
        prices = await get_latest_prices(tickers)
        print("Prices fetched")

    for ticker in tickers:
        print(f"Processing {ticker}")
        if prices.empty:
            df = prices[prices["symbol"] == ticker]
            if df.empty:
                print(f"No price data for {ticker}, skipping")
                continue
            row = df.iloc[-1]

            await insert_actual(ticker, row)
        await trim_actuals(ticker)
        await trim_predictions(ticker)
        await insert_prediction(ticker, tomorrow, all_models) 
        await calculate_and_store_daily_mae(ticker, today)

    await database.disconnect()
    print("Daily job finished successfully.")

# ----------------- Run ----------------- #
if __name__ == "__main__":
    import asyncio
    asyncio.run(run_daily_job())
