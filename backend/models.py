from sqlalchemy import Table, Column, Integer, String, Float, Date, UniqueConstraint
from database import metadata, engine

actuals = Table(
  "actuals",
  metadata,
  Column("id", Integer, primary_key=True),
  Column("ticker", String, index=True),
  Column("date", Date),
  Column("open", Float),
  Column("high", Float),
  Column("low", Float),
  Column("close", Float),
  Column("volume", Float),
  UniqueConstraint("ticker", "date", name="uix_ticker_date_prediction"),
)

predictions = Table(
    "predictions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("ticker", String, index=True),
    Column("date", Date),
    Column("prediction", Float),
    UniqueConstraint("ticker", "date", name="uix_ticker_date_prediction"),
)

maes = Table(
  "maes",
  metadata,
  Column("ticker", String, primary_key=True),
  Column("mae", Float, index=True),
)

days = Table(
  "days",
  metadata,
  Column("id", Integer, primary_key=True),
  Column("date", Date, index=True)
)

daily_maes = Table(
    "daily_maes",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("ticker", String, index=True),
    Column("date", Date, index=True),
    Column("mae", Float, index=True),
    UniqueConstraint("ticker", "date", name="uix_daily_mae_ticker_date"),
)

metadata.create_all(engine)
