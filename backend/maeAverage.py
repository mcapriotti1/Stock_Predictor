from models import maes
from sqlalchemy import select
from database import database
import asyncio

async def average():
    

  query = select(maes.c.mae)

  mae_average = await database.fetch_all(query) 

  total = 0
  for m in mae_average:
    avg = m["mae"]
    total += avg

  print(avg/len(mae_average))



if __name__ == "__main__":
    asyncio.run(average())