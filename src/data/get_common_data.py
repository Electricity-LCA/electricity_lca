import datetime
from dataclasses import dataclass

import pandas as pd
import sqlalchemy

from sqlalchemy.orm import sessionmaker


@dataclass
class BasicDataCache:
    generation_types: pd.DataFrame
    generation_type_mappings: pd.DataFrame
    regions: pd.DataFrame
    retrieved_timestamp: datetime.datetime


def load_common_data_from_db(sql_engine):
    generation_types = pd.read_sql(sqlalchemy.text('SELECT * FROM public."ElectricityGenerationTypes"'), sql_engine)
    generation_type_mappings = pd.read_sql(sqlalchemy.text('SELECT * FROM public."ElectricityGenerationTypesMapping"'), sql_engine)
    regions = pd.read_sql(sqlalchemy.text('SELECT * FROM public."Regions"'), sql_engine)
    retrieved_timestamp = datetime.datetime.now(datetime.timezone.utc)

    return BasicDataCache(generation_types=generation_types, regions=regions, retrieved_timestamp=retrieved_timestamp,generation_type_mappings=generation_type_mappings)
