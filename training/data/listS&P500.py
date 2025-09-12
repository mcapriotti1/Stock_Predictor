import os

folder_path = "FinanceData"

files = os.listdir(folder_path)

tickers = []
for file in files:
    if "_" in file:  # make sure there is an underscore
        ticker = file.split("_")[0]
        tickers.append(ticker)

tickers = list(set(tickers))

print("Tickers found:", tickers)
