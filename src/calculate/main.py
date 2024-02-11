import datetime

import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, Response
from fastapi.openapi.docs import get_swagger_ui_html

import uvicorn
import sqlalchemy as sqla
from sqlalchemy.orm import sessionmaker
import os

from src.orm.base import ElectricityGenerationNew

from src.data.get_common_data import load_common_data_from_db


app = FastAPI()

@app.get('/calculate')
async def calculate_impacts(date_start,region_code: int):
    load_dotenv()

    HOST = os.getenv('ELEC_LCA_HOST')
    DB_NAME = os.getenv('ELEC_LCA_DB_NAME')
    USER = os.getenv('ELEC_LCA_USER')
    PASSWORD = os.getenv('ELEC_LCA_PASSWORD')


    engine = sqla.create_engine(sqla.engine.url.URL.create(
        drivername='postgresql',
        host=HOST,
        database=DB_NAME,
        username=USER,
        password=PASSWORD
    ))
    session_obj = sessionmaker(bind=engine)
    with session_obj() as session:
        query = (session.query(ElectricityGenerationNew).limit(10))

        df = pd.read_sql(query.statement, session.bind)

        return Response(df.to_json(), media_type="application/json")

@app.get('/docs')
def get_docs():
    return get_swagger_ui_html(openapi_url='/openapi.json')


if __name__ == '__main__':
    uvicorn.run(app, port=8000)
