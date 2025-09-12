import numpy as np
from database import database
from models import actuals

async def get_actuals_for_ticker(ticker: str, prediction_date):
    await database.connect()
    query = (
        actuals.select()
        .where(
            (actuals.c.ticker == ticker) &
            (actuals.c.date < prediction_date)
        )
        .order_by(actuals.c.date)
    )    
    results = await database.fetch_all(query)
    await database.disconnect()
    actuals_list = [dict(row) for row in results]
    return actuals_list

async def get_data_for_prediction(ticker: str, prediction_date):
    actuals_list = await get_actuals_for_ticker(ticker, prediction_date)
    if not actuals_list:
        return None

    data_array = np.array([
        [row["close"], row["open"], row["high"], row["low"], row["volume"]]
        for row in actuals_list
    ])
    return data_array

async def run_prediction(ticker, all_models, predictionDate, window_size=30):
    data = await get_data_for_prediction(ticker, predictionDate)

    if ticker not in all_models:
        raise ValueError(f"No saved model for {ticker}")
    
    model_data = all_models[ticker]
    model = model_data["model"]
    scaler = model_data["scaler"]
    close_scaler = model_data["close_scaler"]
    
    data_scaled = scaler.transform(data)
    
    if len(data_scaled) < window_size:
        raise ValueError(f"Not enough data rows ({len(data_scaled)}) for window size {window_size}")
    
    last_seq = data_scaled[-window_size:]
    last_seq = np.expand_dims(last_seq, axis=0)
    
    pred_scaled = model.predict(last_seq, verbose=0)
    predicted_close = close_scaler.inverse_transform(pred_scaled)[0][0]
    
    return float(predicted_close), float(model_data["mae_pct"])