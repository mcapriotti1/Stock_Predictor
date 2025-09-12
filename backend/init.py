from yahooquery import Ticker
from database import database
from models import actuals, predictions, maes, days
from datetime import date, timedelta
from backend.myModel import run_prediction
import joblib
import asyncio
import sqlite3
import pandas_market_calendars as mcal
import pandas as pd
from sqlalchemy import select, asc, desc
from backend.dailyJob import calculate_and_store_daily_mae, get_today, trim_actuals

TICKERS = ['MMM', 'LEG', 'ORCL', 'PNC', 'NVDA', 'NEM', 'HRB', 'TDG', 'ALB', 'DIS', 'D', 'PPG', 'DG', 'UDR', 'DTE', 'HUM', 'HII', 'ECL', 'AME', 'CRM', 'TRIP', 'DUK', 'MDT', 'CINF', 'INTC', 'FE', 'BXP', 'FOX', 'NSC', 'PG', 'NAVI', 'ED', 'NTAP', 'BLK', 'ILMN', 'VLO', 'AIV', 'NUE', 'CAH', 'KR', 'MAS', 'WMB', 'SPGI', 'CNC', 'L', 'BAC', 'LOW', 'COF', 'HSY', 'ALLE', 'ADBE', 'TRV', 'BA', 'APTV', 'HBAN', 'PEP', 'LRCX', 'PRU', 'CTSH', 'ALGN', 'MS', 'M', 'BHF', 'CI', 'RSG', 'FAST', 'CVS', 'VRSK', 'CBOE', 'MAC', 'O', 'AFL', 'JBHT', 'VFC', 'FDX', 'ABT', 'SNPS', 'IQV', 'IDXX', 'HP', 'NOC', 'NWSA', 'AYI', 'ITW', 'MTB', 'PEG', 'SCHW', 'EMR', 'GWW', 'AMT', 'GE', 'TROW', 'SBUX', 'COO', 'KMI', 'GLW', 'HPE', 'AMAT', 'ADSK', 'ZBH', 'CL', 'DAL', 'FMC', 'GM', 'T', 'REGN', 'SLB', 'ULTA', 'KIM', 'SNA', 'ROP', 'AES', 'HOLX', 'JCI', 'SIG', 'AMGN', 'ETN', 'MSFT', 'LKQ', 'LH', 'BBT', 'FRT', 'NWL', 'DVN', 'WU', 'BEN', 'MOS', 'LYB', 'FOXA', 'COST', 'BK', 'FFIV', 'MAT', 'STT', 'VZ', 'WDC', 'SLG', 'NTRS', 'KLAC', 'SWK', 'GT', 'MLM', 'PLD', 'RRC', 'PYPL', 'HBI', 'NCLH', 'BDX', 'SPG', 'AVGO', 'STZ', 'AVB', 'MTD', 'SJM', 'ADM', 'AIZ', 'CVX', 'MCHP', 'TGT', 'OKE', 'VTR', 'OXY', 'MDLZ', 'HAS', 'PNR', 'HON', 'MAA', 'RCL', 'MA', 'WYNN', 'MCO', 'INCY', 'ADP', 'CME', 'COTY', 'MRK', 'SEE', 'SYK', 'TJX', 'DE', 'AEE', 'CCI', 'EXC', 'QCOM', 'CPB', 'GOOGL', 'ROST', 'STX', 'FCX', 'GILD', 'WEC', 'TSN', 'CSX', 'PM', 'VRSN', 'NWS', 'KEY', 'CSCO', 'F', 'TXT', 'EQIX', 'EL', 'FTI', 'MET', 'DXC', 'GIS', 'WM', 'FLR', 'GS', 'ALL', 'UNP', 'TXN', 'IBM', 'ETR', 'KHC', 'LNT', 'AAP', 'EA', 'PHM', 'USB', 'NEE', 'HLT', 'RF', 'WHR', 'WAT', 'CMCSA', 'JNJ', 'ZION', 'UHS', 'GOOG', 'XOM', 'CHRW', 'HOG', 'KO', 'IT', 'PNW', 'IP', 'K', 'IPG', 'AMP', 'BBY', 'ORLY', 'PPL', 'EOG', 'PFG', 'FTV', 'KMB', 'SYF', 'FLS', 'SHW', 'DLR', 'AVY', 'CMA', 'CDNS', 'AWK', 'KMX', 'DOV', 'MKC', 'MPC', 'PVH', 'EXR', 'UAL', 'DHR', 'PH', 'CMS', 'LMT', 'EXPD', 'MMC', 'PKG', 'MNST', 'GPC', 'EQR', 'AMG', 'APA', 'PCAR', 'MCK', 'ICE', 'MCD', 'ES', 'AZO', 'AJG', 'BSX', 'IVZ', 'GD', 'NI', 'LLY', 'CAG', 'EFX', 'UNH', 'AIG', 'ADI', 'PSA', 'PRGO', 'MHK', 'XRAY', 'AOS', 'OMC', 'TMO', 'NFLX', 'PCG', 'MGM', 'TSCO', 'TEL', 'YUM', 'HCA', 'EMN', 'CB', 'RMD', 'XRX', 'WFC', 'LNC', 'FIS', 'EIX', 'GRMN', 'CMG', 'MAR', 'ROK', 'HAL', 'CHD', 'ARE', 'FITB', 'SRE', 'BWA', 'IFF', 'IRM', 'ACN', 'GPN', 'CAT', 'UNM', 'MU', 'CF', 'DLTR', 'RHI', 'V', 'ISRG', 'HD', 'MSI', 'UA', 'XEL', 'COP', 'HRL', 'LEN', 'VRTX', 'HST', 'URI', 'PWR', 'AAPL', 'EW', 'EXPE', 'CTAS', 'EQT', 'REG', 'CHTR', 'CLX', 'AMD', 'AEP', 'UPS', 'APH', 'DHI', 'XYL', 'PSX', 'SO', 'VMC', 'NOV', 'AXP', 'DVA', 'NKE', 'NRG', 'EBAY', 'AAL', 'LUV', 'RL', 'ALK', 'DRI', 'HSIC', 'PAYX', 'APD', 'JPM', 'NDAQ', 'A', 'AKAM', 'MO', 'DGX', 'WY', 'SYY', 'IR', 'HPQ', 'VNO', 'BAX', 'INTU', 'AON', 'TPR', 'RJF', 'PGR', 'CCL', 'WMT', 'ESS', 'UAA', 'BMY', 'CNP', 'AMZN', 'PFE', 'BIIB', 'HIG', 'QRVO', 'TAP', 'ZTS', 'C', 'KSS', 'SBAC', 'CMI', 'ABBV', 'CFG', 'SWKS']

async def init_trading_days(years_ahead=10):
  nyse = mcal.get_calendar("NYSE")
  today = pd.Timestamp(date.today())
  start = today - timedelta(20)
  end = today + pd.DateOffset(years=years_ahead)

  schedule = nyse.valid_days(start_date=start, end_date=end)

  values = [{"date": d.date()} for d in schedule]

  try:
    await database.execute_many(query=days.insert(), values=values)
    print(f"Inserted {len(values)} trading days into DB")
  except Exception as e:
    print(f"Could not insert trading days: {e}")

async def grab_last_days():
    ticker_obj = Ticker("AAPL")
    prices = ticker_obj.history(period="1d").reset_index()
    last_date = prices['date'].iloc[-1]

    today = last_date
    if not today:
        print("No trading days found in DB!")
        return None
    
    next_day_query = (
        select(days.c.date)
        .where(days.c.date > today)
        .order_by(asc(days.c.date))
        .limit(1)
    )

    trading_day = await database.fetch_one(next_day_query)    

    next_trading_day = trading_day["date"]

    prev_days_query = (
        select(days.c.date)
        .where(days.c.date < next_trading_day)
        .order_by(desc(days.c.date))
        .limit(20)
    )
    prev_days = await database.fetch_all(prev_days_query)

    prev_days = [row["date"] for row in reversed(prev_days)]



    return next_trading_day, prev_days

async def init_db():
    await database.connect()

    print("Checking if DB needs initialization...")
    query = actuals.select().where(actuals.c.ticker == TICKERS[0])
    existing = await database.fetch_one(query)
    if existing:
      print("DB already initialized, skipping init.")
      return

    print("Initializing DB with last 30 days of actuals and predictions...")

    
    await init_trading_days()

    tommorow, past = await grab_last_days()

    try:
      all_models = joblib.load("all_models.joblib")
      print("Model File Loaded")
    except FileNotFoundError:
      print("Model File NOT FOUND???")

    for ticker in TICKERS:
        print(f"Initializing {ticker}...")

        ticker_obj = Ticker(ticker)
        prices = ticker_obj.history(period="100d").reset_index() 

        for _, row in prices.iterrows():
            day = row["date"].date() if hasattr(row["date"], "date") else row["date"]

            try:
              query = actuals.insert().values(
                  ticker=ticker,
                  date=day,
                  open=row["open"],
                  close=row["close"],
                  high=row["high"],
                  low=row["low"],
                  volume=row["volume"]
              )
              await database.execute(query)
            except sqlite3.IntegrityError:
              print(f"\tRow for {ticker} on {day} already exists, skipping.")

        # Last 10 Predictions Loop
        for d in past:
          prediction, mae = await run_prediction(ticker, all_models, d)
          try:
            query = predictions.insert().values(
                    ticker=ticker,
                    date=d,
                    prediction=prediction
                )
            await database.execute(query)
          except sqlite3.IntegrityError:
            print(f"\tPrediction for {ticker} on {tommorow} already exists, skipping.")


        #Tommorow       
        prediction, mae = await run_prediction(ticker, all_models, tommorow)
        
        try:
          query = predictions.insert().values(
                  ticker=ticker,
                  date=tommorow,
                  prediction=prediction
              )
          await database.execute(query)
        except sqlite3.IntegrityError:
          print(f"\tPrediction for {ticker} on {tommorow} already exists, skipping.")

        try:
          query = maes.insert().values(
                  ticker=ticker,
                  mae=mae,
              )
          await database.execute(query)
        except sqlite3.IntegrityError:
          print(f"\tMAE for {ticker} already exists, skipping.")

        today = get_today()
        await calculate_and_store_daily_mae(ticker, today)
        await trim_actuals(ticker)
    
    await database.disconnect()
    print("Database initialized with last 30 days of data.")

if __name__ == "__main__":
    asyncio.run(init_db())
