import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import os

# Create sequences
def create_sequences(data, window_size=30):
    X, y = [], []
    for i in range(len(data) - window_size):
        X.append(data[i:i+window_size])
        y.append(data[i+window_size, 0])
    return np.array(X), np.array(y)

def train_lstm_for_ticker(ticker, window_size=30, min_rows=1255):
    try:
        filepath = f"data/FinanceData/{ticker}_history.csv"
        if not os.path.exists(filepath):
            print(f"File not found for {ticker}, skipping...")
            return None

        df = pd.read_csv(filepath).sort_values("date")

        if len(df) < min_rows:
            print(f"{ticker} has only {len(df)} rows (<{min_rows}), skipping...")
            return None

        prices = df[["close", "open", "high", "low", "volume"]].values

        scaler = MinMaxScaler()
        prices_scaled = scaler.fit_transform(prices)

        X, y = create_sequences(prices_scaled, window_size)

        if len(X) < 60:  
            print(f"Not enough sequences for {ticker}, skipping...")
            return None

        split_index = int(len(X) * 0.8)
        X_train, y_train = X[:split_index], y[:split_index]
        X_test, y_test = X[split_index:], y[split_index:]

        if len(X_test) == 0:
            print(f"No test data for {ticker}, skipping...")
            return None

        model = Sequential([
            LSTM(50, activation='tanh', input_shape=(window_size, X_train.shape[2])),
            Dense(1)
        ])
        model.compile(optimizer='adam', loss='mse')

        model.fit(X_train, y_train, epochs=50, batch_size=32, verbose=0)

        pred_scaled = model.predict(X_test, verbose=0)

        close_scaler = MinMaxScaler()
        close_scaler.fit(df[['close']].values)

        predictions = close_scaler.inverse_transform(pred_scaled)
        y_actual = close_scaler.inverse_transform(y_test.reshape(-1, 1))

        mae = mean_absolute_error(y_actual, predictions)
        mae_pct = np.mean(np.abs(y_actual - predictions) / y_actual) * 100

        print(f"{ticker} trained | Rows: {len(df)} | MAE: {mae:.2f}, MAE%: {mae_pct:.2f}%")

        return {
            "ticker": ticker,
            "model": model,
            "scaler": scaler,
            "close_scaler": close_scaler,
            "mae": mae,
            "mae_pct": mae_pct
        }

    except Exception as e:
        print(f"Error training {ticker}: {e}")
        return None


def train_all_tickers(tickers, save_file="all_models.joblib"):
    all_models = {}
    invalid_tickers = []

    for ticker in tickers:
        print(f"Training model for {ticker}...")
        result = train_lstm_for_ticker(ticker)
        if result is None:
            invalid_tickers.append(ticker)
        else:
            all_models[ticker] = result

    joblib.dump(all_models, save_file)
    print(f"All models saved to {save_file}")

    if invalid_tickers:
        print("\nInvalid/Skipped Tickers:")
        print(invalid_tickers)


tickers = ['MMM', 'LEG', 'ORCL', 'PNC', 'NVDA', 'NEM', 'HRB', 'TDG', 'ALB', 'DIS', 'D', 'PPG', 'DG', 'UDR', 'DTE', 'HUM', 'HII', 'ECL', 'AME', 'CRM', 'TRIP', 'DUK', 'MDT', 'CINF', 'INTC', 'FE', 'BXP', 'FOX', 'NSC', 'PG', 'NAVI', 'ED', 'NTAP', 'BLK', 'ILMN', 'VLO', 'AIV', 'NUE', 'CAH', 'KR', 'MAS', 'WMB', 'SPGI', 'CNC', 'L', 'BAC', 'LOW', 'COF', 'HSY', 'ALLE', 'ADBE', 'TRV', 'BA', 'APTV', 'HBAN', 'PEP', 'LRCX', 'PRU', 'CTSH', 'ALGN', 'MS', 'M', 'BHF', 'CI', 'RSG', 'FAST', 'CVS', 'VRSK', 'CBOE', 'MAC', 'O', 'AFL', 'JBHT', 'VFC', 'FDX', 'ABT', 'SNPS', 'IQV', 'IDXX', 'HP', 'NOC', 'NWSA', 'AYI', 'ITW', 'MTB', 'PEG', 'SCHW', 'EMR', 'GWW', 'AMT', 'GE', 'TROW', 'SBUX', 'COO', 'KMI', 'GLW', 'HPE', 'AMAT', 'ADSK', 'ZBH', 'CL', 'DAL', 'FMC', 'GM', 'T', 'REGN', 'SLB', 'ULTA', 'KIM', 'SNA', 'ROP', 'AES', 'HOLX', 'JCI', 'SIG', 'AMGN', 'ETN', 'MSFT', 'LKQ', 'LH', 'BBT', 'FRT', 'NWL', 'DVN', 'WU', 'BEN', 'MOS', 'LYB', 'FOXA', 'COST', 'BK', 'FFIV', 'MAT', 'STT', 'VZ', 'WDC', 'SLG', 'NTRS', 'KLAC', 'SWK', 'GT', 'MLM', 'PLD', 'RRC', 'PYPL', 'HBI', 'NCLH', 'BDX', 'SPG', 'AVGO', 'STZ', 'AVB', 'MTD', 'SJM', 'ADM', 'AIZ', 'CVX', 'MCHP', 'TGT', 'OKE', 'VTR', 'OXY', 'MDLZ', 'HAS', 'PNR', 'HON', 'MAA', 'RCL', 'MA', 'WYNN', 'MCO', 'INCY', 'ADP', 'CME', 'COTY', 'MRK', 'SEE', 'SYK', 'TJX', 'DE', 'AEE', 'CCI', 'EXC', 'QCOM', 'CPB', 'GOOGL', 'ROST', 'STX', 'FCX', 'GILD', 'WEC', 'TSN', 'CSX', 'PM', 'VRSN', 'NWS', 'KEY', 'CSCO', 'F', 'TXT', 'EQIX', 'EL', 'FTI', 'MET', 'DXC', 'GIS', 'WM', 'FLR', 'GS', 'ALL', 'UNP', 'TXN', 'IBM', 'ETR', 'KHC', 'LNT', 'AAP', 'EA', 'PHM', 'USB', 'NEE', 'HLT', 'RF', 'WHR', 'WAT', 'CMCSA', 'JNJ', 'ZION', 'UHS', 'GOOG', 'XOM', 'CHRW', 'HOG', 'KO', 'IT', 'PNW', 'IP', 'K', 'IPG', 'AMP', 'BBY', 'ORLY', 'PPL', 'EOG', 'PFG', 'FTV', 'KMB', 'SYF', 'FLS', 'SHW', 'DLR', 'AVY', 'CMA', 'CDNS', 'AWK', 'KMX', 'DOV', 'MKC', 'MPC', 'PVH', 'EXR', 'UAL', 'DHR', 'PH', 'CMS', 'LMT', 'EXPD', 'MMC', 'PKG', 'MNST', 'GPC', 'EQR', 'AMG', 'APA', 'PCAR', 'MCK', 'ICE', 'MCD', 'ES', 'AZO', 'AJG', 'BSX', 'IVZ', 'GD', 'NI', 'LLY', 'CAG', 'EFX', 'UNH', 'AIG', 'ADI', 'PSA', 'PRGO', 'MHK', 'XRAY', 'AOS', 'OMC', 'TMO', 'NFLX', 'PCG', 'MGM', 'TSCO', 'TEL', 'YUM', 'HCA', 'EMN', 'CB', 'RMD', 'XRX', 'WFC', 'LNC', 'FIS', 'EIX', 'GRMN', 'CMG', 'MAR', 'ROK', 'HAL', 'CHD', 'ARE', 'FITB', 'SRE', 'BWA', 'IFF', 'IRM', 'ACN', 'GPN', 'CAT', 'UNM', 'MU', 'CF', 'DLTR', 'RHI', 'V', 'ISRG', 'HD', 'MSI', 'UA', 'XEL', 'COP', 'HRL', 'LEN', 'VRTX', 'HST', 'URI', 'PWR', 'AAPL', 'EW', 'EXPE', 'CTAS', 'EQT', 'REG', 'CHTR', 'CLX', 'AMD', 'AEP', 'UPS', 'APH', 'DHI', 'XYL', 'PSX', 'SO', 'VMC', 'NOV', 'AXP', 'DVA', 'NKE', 'NRG', 'EBAY', 'AAL', 'LUV', 'RL', 'ALK', 'DRI', 'HSIC', 'PAYX', 'APD', 'JPM', 'NDAQ', 'A', 'AKAM', 'MO', 'DGX', 'WY', 'SYY', 'IR', 'HPQ', 'VNO', 'BAX', 'INTU', 'AON', 'TPR', 'RJF', 'PGR', 'CCL', 'WMT', 'ESS', 'UAA', 'BMY', 'CNP', 'AMZN', 'PFE', 'BIIB', 'HIG', 'QRVO', 'TAP', 'ZTS', 'C', 'KSS', 'SBAC', 'CMI', 'ABBV', 'CFG', 'SWKS']
train_all_tickers(tickers)
