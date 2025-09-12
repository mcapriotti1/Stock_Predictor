import pandas as pd
from yahooquery import Ticker
from concurrent.futures import ThreadPoolExecutor
import csv
import os

tickers = []
badTickers = []
folder = "FinanceData"
SP500 = "cleanS&P500Data.csv"

with open(SP500, mode ='r')as file:
  csvFile = csv.reader(file)
  for lines in csvFile:
        tickers.append(lines[0])

def retrieve_data(t, rows=1255):
    filename = t + "_history.csv"
    if os.path.exists(folder + "/" + filename):
        print(t, "Already Processed")
        return
    print("Processing", t)
    ticker = Ticker(t)

    hist = ticker.history(period="5y")

    hist = hist.reset_index()
    if hist.empty:
        print("\tEmpty Data Frame?")
        badTickers.append(t)
        return

    df = hist[["date", "open", "high", "low", "close", "volume"]]

    if len(df) < rows:
        print(f"\tIncorrect Amount of Rows ({len(df)} rows), skipping {t}")
        badTickers.append(t)
        return

    df.to_csv(folder + "/" + t + "_history.csv", index=False)

    print("Saved", t ,"history to " + filename)

with ThreadPoolExecutor(max_workers=10) as executor:
    executor.map(retrieve_data, tickers)