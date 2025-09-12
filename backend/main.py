from fastapi import FastAPI
from database import database
from models import predictions, actuals, maes, daily_maes
from datetime import date, timedelta
from sqlalchemy import select, desc, asc
from init import init_db
import asyncio

app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()
    asyncio.create_task(init_db())

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/")
async def read_root():
    query = select(daily_maes.c.ticker, daily_maes.c.mae).order_by(asc(daily_maes.c.mae))
    tickersResult = await database.fetch_all(query)

    return {"tickers": tickersResult}

@app.get("/predict/{ticker}")
async def predict_stock(ticker: str):    
    query = select(predictions.c.date, predictions.c.prediction).where((predictions.c.ticker == ticker))
    predictionResult = await database.fetch_all(query)

    query = select(actuals.c.date, actuals.c.close).where(actuals.c.ticker == ticker)
    actualResult = await database.fetch_all(query)

    query = select(maes.c.mae).where(maes.c.ticker == ticker)
    maeResult = await database.fetch_one(query)

    query = select(daily_maes.c.mae).where(daily_maes.c.ticker == ticker).order_by(desc(daily_maes.c.date))
    dailyMaeResult = await database.fetch_one(query)
    
    if predictionResult and actualResult and maeResult and dailyMaeResult:
        return {"ticker": ticker, "predictions": predictionResult, "actuals": actualResult, "mae": round(maeResult["mae"], 2), "dailyMae": dailyMaeResult["mae"]}
    
    return {"error": "Prediction not yet generated for today."}
