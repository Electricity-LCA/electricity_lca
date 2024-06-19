import asyncio

from src.microservice.generation import get_earliest_date_for_region
import sqlalchemy as sqla
import os
from dotenv import load_dotenv



load_dotenv()
HOST = os.getenv('ELEC_LCA_HOST')
DB_NAME = os.getenv('ELEC_LCA_DB_NAME')
USER = os.getenv('ELEC_LCA_USER')
PASSWORD = os.getenv('ELEC_LCA_PASSWORD')
PORT = os.getenv('ELEC_LCA_DB_PORT')

# Connect to postgres database
engine = sqla.create_engine(sqla.engine.url.URL.create(
    drivername='postgresql',
    host=HOST,
    database=DB_NAME,
    username=USER,
    password=PASSWORD,
    port=PORT
))

async def main():
    region_code = 'BE'
    date_status = await get_earliest_date_for_region(region_code, engine=engine)
    print(date_status)

loop = asyncio.get_event_loop()
tasks = [loop.create_task(main())]
loop.run_until_complete(asyncio.wait(tasks))
loop.close()
print('Done')