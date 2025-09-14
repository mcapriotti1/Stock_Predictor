# Stock Predictor

A machine learning web app that predicts tomorrow’s stock closing prices for 400+ companies using LSTM models trained on 5 years of historical data, with results displayed in an interactive React + FastAPI dashboard.

---

## About the Project

**Tech Used:** Python, Typescript, React, FastAPI, Sqlite3, CSS

Used Yahooquery to fetch 5 years of daily historical data on stocks. Items inclued were the opening, closing, high, low, and volume. Once the data was cleaned, a Long Short-Term Memory (LSTM) model via TensorFlow was trained on 4 years of the data, the 5th year was used for testing assessed by checking absolute error between the actual and predicted price. The LSTM model takes in the stock data from the past 30 days and returns its prediction of the closing price for the following day. Each stock has its own model which are all saved in all_models.joblib alongside the mean absolute error (MAE) for each stock from 2024-2025. The average of the MAE's from all the stocks over the testing period is 2.76%. When the backend starts, ```init_db()``` runs to initalize the sqlite3 database by inserting the past 40 days of stock history, predictions over the last 10 days, and the MAE. The function ```run_daily_job()``` gathers and inserts the current days actual prices, makes predictions for the next day, and cleans up the old date. FastAPI makes queries to the database which are sent over the frontend. The frontend displays the tickers, implements a search feature, and creates interactive graphs based on the data via chart.js.

## Front Page
<div style="text-align: center">
  <img src="demoVideos\StockDemo_FrontPage.gif" 
     alt="Demo Screenshot" 
     style="display: block; margin: 0 auto;">
</div>

## Forecast Prediction

<div style="text-align: center">
  <img src="demoVideos\StockDemo_Forecast.gif" 
     alt="Demo Screenshot" 
     style="display: block; margin: 0 auto;">
</div>

## Past Prediction

<div style="text-align: center">
  <img src="demoVideos\StockDemo_Past.gif" 
     alt="Demo Screenshot" 
     style="display: block; margin: 0 auto;">
</div>

## Running Instructions

### 1. Clone the Repository  
```bash
git clone https://github.com/mcapriotti1/stock_predictor.git
cd stock_predictor
```

### 2. Backend Setup
```bash
cd backend
python -m venv predictor
source ./predictor/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 4. Training Setup (Optional if Retraining Model)
```bash
cd training
cd train
python LSTM.py


