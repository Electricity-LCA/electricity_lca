import logging
import os
from typing import Any

import pandas as pd
import sqlalchemy as sqla
from dotenv import load_dotenv
from fastapi import FastAPI, Response
from fastapi.openapi.docs import get_swagger_ui_html
import uvicorn

from src.data.get_common_data import load_common_data_from_db
from src.microservice.calculate import ImpactResultSchema, calculate_impact_df
from src.microservice.constants import ServerError
from src.microservice.generation import get_electricity_generation_df, get_earliest_date_for_region

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
cache = load_common_data_from_db(sql_engine=engine)

app = FastAPI()


def cache_data(f):
    cache = {}

    def foo(x):
        if x not in cache:
            cache[x] = f(x)
        return cache[x]

    return foo


@app.get('/docs')
def get_docs():
    return get_swagger_ui_html(title='API documentation for elc_lca')


@app.get('/list_regions')
async def list_regions():
    regions_df = cache.regions
    return Response(regions_df.to_json(orient='records'), media_type="application/json")

@app.get('/list_generation_types')
async def list_generation_types():
    generation_types_df = cache.generation_types
    return Response(generation_types_df.to_json(orient='records'), media_type="application/json")

@app.get('/list_generation_type_mappings')
async def list_generation_type_mappings():
    generation_type_mappings_df = cache.generation_type_mappings
    return Response(generation_type_mappings_df.to_json(orient='records'), media_type="application/json")


@app.get('/earliest_generation_datestamp')
async def get_earliest_datestamp_for_region(region_code: str):
    """
     If there is no data for a given region returns an empty data frame with a 204 status code

    @param region_code:
    @return:
    """
    try:
        date_or_status = get_earliest_date_for_region(region_code, engine=engine)
    except TypeError as e:
        return Response(status_code=400, content=str(e))
    except ValueError as e:
        return Response(status_code=422, content=str(e))
    except ServerError as e:
        return Response(status_code=500, content=str(e))
    if date_or_status == 204:
        return Response(status_code=204)

    return Response(date_or_status,status_code=200)


@app.get('/generation')
async def get_electricity_generation(date_start, region_code: str, generation_type_id: int):
    try:
        df = await get_electricity_generation_df(date_start, None, region_code, generation_type_id, engine=engine)
    except TypeError as e:
        return Response(status_code=400, content=str(e))
    except ValueError as e:
        return Response(status_code=422, content=str(e))
    except ServerError as e:
        return Response(status_code=500, content=str(e))
    if not isinstance(df, pd.DataFrame):
        return Response(status_code=500)
    return Response(df.to_json(orient='records'), media_type="application/json")


@app.get('/calculate', response_model=ImpactResultSchema)
async def calculate_impact(date_start, region_code: str, generation_type_id: int)->Any:
    try:
        impact_df = await calculate_impact_df(date_start, region_code, generation_type_id,engine=engine)
    except TypeError as e:
        return Response(status_code=400, content=str(e))
    except ValueError as e:
        return Response(status_code=422, content=str(e))
    except ServerError as e:
        return Response(status_code=500, content=str(e))
    if not isinstance(impact_df, pd.DataFrame):
        return Response(status_code=500)
    return Response(impact_df.to_json(orient='records'), media_type='text/json')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,filename='api.log')
    uvicorn.run(app, port=8000)
