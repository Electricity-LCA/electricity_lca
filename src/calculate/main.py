import logging
import os

import pandas as pd
import sqlalchemy as sqla
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI, Response
from fastapi.openapi.docs import get_swagger_ui_html
import uvicorn


from src.data.get_common_data import load_common_data_from_db
from src.orm.base import ElectricityGenerationNew, Regions

ROW_LIMIT = 500
load_dotenv()
HOST = os.getenv('ELEC_LCA_HOST')
DB_NAME = os.getenv('ELEC_LCA_DB_NAME')
USER = os.getenv('ELEC_LCA_USER')
PASSWORD = os.getenv('ELEC_LCA_PASSWORD')

# Connect to postgres database
engine = sqla.create_engine(sqla.engine.url.URL.create(
    drivername='postgresql',
    host=HOST,
    database=DB_NAME,
    username=USER,
    password=PASSWORD
))
cache = load_common_data_from_db(sql_engine=engine)

app = FastAPI()


@app.get('/docs')
def get_docs():
    return get_swagger_ui_html(title='API documentation for elc_lca')

@app.get('/generation')
async def get_electricity_generation(date_start, region_code: str, generation_type_id: int):
    load_dotenv()

    HOST = os.getenv('ELEC_LCA_HOST')
    DB_NAME = os.getenv('ELEC_LCA_DB_NAME')
    USER = os.getenv('ELEC_LCA_USER')
    PASSWORD = os.getenv('ELEC_LCA_PASSWORD')

    if not isinstance(region_code, str):
        return None

    engine = sqla.create_engine(sqla.engine.url.URL.create(
        drivername='postgresql',
        host=HOST,
        database=DB_NAME,
        username=USER,
        password=PASSWORD
    ))
    session_obj = sessionmaker(bind=engine)
    with session_obj() as session:
        region_id_query = session.query(Regions.Id).where(Regions.Code == region_code).limit(1)
        region_id_df = pd.read_sql(region_id_query.statement, session.bind)
        if region_id_df is None or region_id_df.shape[0] != 1:
            raise ValueError(f'Region Code `{region_code}` could not be found in database')

        region_id = int(region_id_df.iat[0, 0])
        logging.warning(f'REGION IS {region_id}')

        query = (session.query(ElectricityGenerationNew)
                 .where(ElectricityGenerationNew.GenerationTypeId == generation_type_id)
                 .where(ElectricityGenerationNew.RegionId == region_id)
                 .limit(ROW_LIMIT))

        df = pd.read_sql(query.statement, session.bind)

        return Response(df.to_json(), media_type="application/json")


if __name__ == '__main__':
    uvicorn.run(app, port=8000)


